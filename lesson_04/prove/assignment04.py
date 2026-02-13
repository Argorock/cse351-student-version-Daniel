"""
Course    : CSE 351
Assignment: 04
Student   : <your name here>

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0
"""

import time
from common import *
import queue
from threading import Thread
from cse351 import *

THREADS = 40
WORKERS = 10
RECORDS_TO_RETRIEVE = 5000


# ---------------------------------------------------------------------------
def retrieve_weather_data(command_que, result_que):
    while True:
        cmd = command_que.get()
        if cmd == "DONE":
            break

        city, recno = cmd
        url = f"{TOP_API_URL}/record/{city}/{recno}"

        time.sleep(0.001)

        while True:
            data = get_data_from_server(url)

            if data is not None and "temp" in data:
                result_que.put((city, recno, data["date"], data["temp"]))
                break

            time.sleep(0.001)


# ---------------------------------------------------------------------------
class Worker(Thread):
    def __init__(self, result_que, noaa):
        super().__init__()
        self.result_que = result_que
        self.noaa = noaa

    def run(self):
        while True:
            item = self.result_que.get()
            if item == "DONE":
                break

            city, recno, date, temp = item

            with self.noaa.locks[city]:
                self.noaa.city_dict[city][recno] = (date, temp)


# ---------------------------------------------------------------------------
class NOAA:
    def __init__(self):
        import threading
        self.city_dict = {}
        self.locks = {}

        for city in CITIES:
            self.city_dict[city] = [None] * RECORDS_TO_RETRIEVE
            self.locks[city] = threading.Lock()

    def get_temp_details(self, city):
        temps = [item[1] for item in self.city_dict[city] if item is not None]
        return sum(temps) / len(temps)


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f"{name:>15}: Records = {city_details[name]['records']:,}")
    print('===================================')

    command_que = queue.Queue(maxsize=10)
    results_que = queue.Queue(maxsize=10)

    # Start retriever threads
    threads = []
    for i in range(THREADS):
        t = Thread(target=retrieve_weather_data, args=(command_que, results_que))
        t.start()
        threads.append(t)

    # Start worker threads
    workers = []
    for _ in range(WORKERS):
        w = Worker(results_que, noaa)
        w.start()
        workers.append(w)

    # Fill the command queue
    records_per_city = RECORDS_TO_RETRIEVE

    for city in CITIES:
        max_recs = min(city_details[city]['records'], records_per_city)
        for recno in range(max_recs):
            command_que.put((city, recno))

    # Tell retrievers to stop
    for _ in range(THREADS):
        command_que.put("DONE")

    # Wait for retrievers
    for t in threads:
        t.join()

    # Tell workers to stop
    for _ in range(WORKERS):
        results_que.put("DONE")

    # Wait for workers
    for w in workers:
        w.join()

    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()