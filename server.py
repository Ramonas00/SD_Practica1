from xmlrpc.server import SimpleXMLRPCServer
#import asyncio
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

    while True:
        packed = r.blpop('queue:email')
        to_send = json.loads(packed[1])
        operacio = to_send["Operacio"]

        if operacio == "suma":
            if to_send["Opcio"] == "wordcount":
                auxSuma = 0
                for x in range(to_send["Lenght"]):
                    packed = r.blpop('suma')
                    to_send = json.loads(packed[1])

            elif to_send["Opcio"] == "countwords":
                auxSuma = 0
                for x in range(to_send["Lenght"]):
                    packed = r.blpop('suma')
                    to_send = json.loads(packed[1])
                    auxSuma += to_send
                

        line = requests.get(to_send["URL"]).text

        if operacio == "wordcount":
            d = len(line.split())
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

        r.rpush(to_send["JOBID"], json.dumps(d))
    
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
        num = int(num) - 1
        if not WORKERS[num]:
            return -1
        
        WORKERS[num].terminate()
        return True


    def list_worker(self):
        ABCD = ''
        for worker in WORKERS:
            ABCD += str(WORKERS[worker]) + "\n"

        return ABCD


    def jobRun(self, opcio, urls):
        global JOBID

        opcio = opcio[4:]
        print (urls)
        urls = urls[1:-1]
        print (urls)
        urls = urls.split(",")
        
        if len(urls) == 1:
            url = urls[0]
            data = {
                'JOBID': JOBID,
                'Operacio': opcio,
                'URL': url
            }
            # ENVIAR A REDIS (JOBID, opcio, url)
            r.rpush('queue:email', json.dumps(data))
        else:
            for x in range(len(urls)):
                url = urls[x]
                data = {
                    'JOBID': 'suma',
                    'Operacio': opcio,
                    'URL': url
                }
                # ENVIAR A REDIS (JOBID, opcio, url)
                r.rpush('queue:email', json.dumps(data))

            data = {
                'JOBID': JOBID,
                'Operacio': 'suma',
                'Opcio': opcio,
                'Lenght': len(urls)
            }
            # ENVIAR A REDIS (JOBID, opcio, url)
            r.rpush('queue:email', json.dumps(data))


        packed = r.blpop(JOBID)
        to_send = json.loads(packed[1])
        JOBID += 1
        return to_send

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
