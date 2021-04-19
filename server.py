from xmlrpc.server import SimpleXMLRPCServer
import logging
import requests
import simplejson as json
import redis
import string
from multiprocessing import Process

WORKERS = {}
WORKER_ID = 0
JOBID = 0

REDIS_PORT = 6379
REDIS_HOST = '127.0.0.1'

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def start_worker(n):
    packed = r.blpop(['queue:email'], 2)
    while True:
        while packed is None:
            asyncio.sleep(1)
            packed = r.blpop(['queue:email'], 2)
        print(packed)

        to_send = json.loads(packed[1])
        operacio = to_send["Operacio"]
        line = requests.get(to_send["URL"]).text

        if operacio == "wordcount":
            wordCount = len(linespilt())
        elif operacio == "countwords":
            d = dict()

            # Remove the leading spaces and newline character /// https://www.geeksforgeeks.org/python-count-occurrences-of-each-word-in-given-text-file-using-dictionary/
            line = line.strip()
  
            # Convert the characters in line to 
            # lowercase to avoid case mismatch
            line = line.lower()
            
            # Remove the punctuation marks from the line
            line = line.translate(line.maketrans("", "", string.punctuation))
            
            # Split the line into words
            words = line.split(" ")
            
            # Iterate over each word in line
            for word in words:
                # Check if the word is already in dictionary
                if word in d:
                    # Increment count of word by 1
                    d[word] = d[word] + 1
                else:
                    # Add the word to dictionary with count 1
                    d[word] = 1
    
    return True

class ServerMethods:


    def crear_worker(self):
        global WORKERS
        global WORKER_ID

        proc = Process(target=start_worker, args=(WORKER_ID,))
        proc.start()
        WORKERS[WORKER_ID] = proc

        WORKER_ID += 1
        return True         # Limitació del xmlrpc


    def delete_worker(self, num):
        if not WORKERS[num]:
            return -1
        
        WORKERS[num].join()
        return True


    def list_worker(self):
        return WORKERS


    def jobRun(opcio, urls):
        global JOBID

        opcio = opcio[4:]
        urls = urls.split(",")
        for x in range(len(urls)):
            url = urls[x]
            data = {
                'JOBID': JOBID,
                'Operacio': opcio,
                'URL': url
            }
            # ENVIAR A REDIS (JOBID, opcio, url)
            r.rpush('queue:email', json.dumps(data))

        JOBID += 1
        return True

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    server = SimpleXMLRPCServer(
        ('localhost', 9000),
        logRequests=True,
    )

    server.register_instance(ServerMethods())

    # Start the server
    try:
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
