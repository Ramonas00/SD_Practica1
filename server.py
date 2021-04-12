from xmlrpc.server import SimpleXMLRPCServer
import logging
import requests
from multiprocessing import Process

WORKERS = {}
WORKER_ID = 0


def start_worker(n):
    #aux = requests.get("http://localhost:8000/Documents/SD/Pract-1/fitxer1.txt")
    #print(aux.text)


class ServerMethods:


    def crear_worker(self):
        global WORKERS
        global WORKER_ID

        proc = Process(target=start_worker, args=(WORKER_ID,))
        proc.start()
        WORKERS[WORKER_ID] = proc

        WORKER_ID += 1


    def delete_worker(self, num):
        if not WORKERS[num]:
            return -1
        
        WORKERS[num].join()


    def list_worker(self):
        return WORKERS


    def list_contents(self, dir_name):
        return dir_name


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
