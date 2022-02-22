import test2
import threading
import time

def ThreadingFunction():
    for i in range(10):
        test2.PrintCanceled()
        time.sleep(0.5)

MyThread = threading.Thread(target=ThreadingFunction)
MyThread.start()
print("hello")
time.sleep(4)
test2.Canceled = True
time.sleep(3)
test2.Canceled = False