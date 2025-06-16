import queue
import threading
import time

audio_queue = queue.Queue()


def scan_queue():
    while True:
        audio = audio_queue.get()
        if audio:
            print(f"Got Audio Sample........ {audio}")
            time.sleep(4)


worker = threading.Thread(target=scan_queue)
worker.start()

audio_queue.put("A")
audio_queue.put("B")
audio_queue.put("C")
audio_queue.put("D")
audio_queue.put("E")


def add_data_to_queue():
    time.sleep(25)
    print("Start Add Data to Queue")
    while True:
        for index in range(10):
            print(f"Adding new data {index}")
            audio_queue.put(f"New {index}")
            print("Added \n\n\n")
            time.sleep(index * 1)


data_worker = threading.Thread(target=add_data_to_queue)
data_worker.start()
