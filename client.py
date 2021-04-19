import xmlrpc.client
import sys


proxy = xmlrpc.client.ServerProxy('http://localhost:9000')
#print(proxy.list_contents(sys.argv[1]))
if (sys.argv[1] == "worker"):
    if (sys.argv[2] == "create"):
        print("Hola")
        proxy.crear_worker()
    if (sys.argv[2] == "delete"):
        proxy.delete_worker(sys.argv[3])
    if (sys.argv[2] == "list"):
        proxy.list_worker()
if (sys.argv[1] == "job"):
    proxy.jobRun(sys.argv[2], sys.argv[3])
