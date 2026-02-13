from multiprocessing import Process, Queue
from threading import Semaphore
from threading import Thread
import time

SEMAPHORE_COUNT = 3
THREAD_COUNT = 20

def f(q):
    q.put("X" * 10) # if this gets too big, it deadlocks

def display(semaphore, name):

    semaphore.acuire()
    print(f"Thread {name}", fluch=True)
    time.sleep(2)

    semaphore.release()

def main():
    queue = Queue()
    p = Process(target=f, args=(queue,))
    p.start()
    print("before join")
    p.join()            # deadlocks here
    print("after join")
    obj = queue.get()
    print("After queue")
    print(obj)



    sem = Semaphore(SEMAPHORE_COUNT)

    threads = [ Thread(target=display, args=(sem, f"{x}")) for x in (THREAD_COUNT + 1)]
    [t.start() for t in threads]
    [t.join() for t in threads]

if __name__ == "__main__":
    main()