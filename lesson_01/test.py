import time
import threading

from cse351 import *

def add_two_to_a_number(x, results):
    answer = x + 2
    results.append(answer)
    # return answer
    

def main():

    results = []
    t = threading.Thread(target=add_two_to_a_number, args=(10, results))

    t.start()

    t.join()

    print(results)
    

if __name__ == "__main__":
    main()