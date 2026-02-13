
import threading
import time


class Display_Hello(threading.Thread):

    def __init__(self, number, name):
        threading.Thread.__init__(self)

        self.number = number
        self.full_name = name

    def run(self):
        time.sleep(self.number)
        print(f"Hello World: {self.number}, {self.full_name}")

if __name__ == "__main__":
    hello1 = Display_Hello(2, "bob")
    hello2 = Display_Hello(1, "mary")

    hello1.happy = True

    hello1.start()
    hello2.start()

    hello1.join()
    hello2.join()