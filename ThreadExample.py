import threading
import multiprocessing as mp
import time


def ThreadingFunction(IncomingQueue):
    while True:
        Message = IncomingQueue.get() # Blocks until there's a message
        if Message[0] == "Print":
            print(Message[1])
        if Message[0] == "Close":
            break

IncomingQueue = mp.Queue()
MyThread = threading.Thread(target=ThreadingFunction,args=(IncomingQueue,))
MyThread.start()

time.sleep(1)

IncomingQueue.put(["Print","Hello World"])
time.sleep(1)
IncomingQueue.put(["Print","Hello Earth"])
time.sleep(1)
IncomingQueue.put(["Print","Hello Brad"])
time.sleep(2)
IncomingQueue.put(["Close"])
time.sleep(1)