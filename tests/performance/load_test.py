import threading
import time

import requests

URL = "http://127.0.0.1:8000/api/v1/screener"

response_times = []


def call_api():
    start = time.perf_counter()

    response = requests.get(URL)

    end = time.perf_counter()

    assert response.status_code == 200

    response_times.append(end - start)


threads = []

overall_start = time.perf_counter()

for _ in range(10):
    thread = threading.Thread(target=call_api)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

overall_end = time.perf_counter()

print(f"Total execution time : {overall_end - overall_start:.3f} seconds")
print(f"Average response time: {sum(response_times)/len(response_times):.3f} seconds")
print(f"Fastest response     : {min(response_times):.3f} seconds")
print(f"Slowest response     : {max(response_times):.3f} seconds")
