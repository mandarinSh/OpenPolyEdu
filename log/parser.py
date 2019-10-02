#!/usr/bin/env python3

import sys, json, threading, time, os, pprint

from multiprocessing import Value
from queue import Queue

unique_keys = set()


def tree_traversal(j):
    for k in j.keys():
        unique_keys.add(k)
        if isinstance(j[k], dict):
            tree_traversal(j[k])


class ThreadClass(threading.Thread):

    def __init__(self, jobs_queue, bytes):
        threading.Thread.__init__(self)
        self.jobs_queue = jobs_queue
        self.bytes = bytes

    def run(self):
        while True:
            # Get from queue job
            line = self.jobs_queue.get()
            json_line = json.loads(line)
            tree_traversal(json_line)
            # signals to queue job is done

            with self.bytes.get_lock():
                self.bytes.value += len(line.encode('utf-8'))
            self.jobs_queue.task_done()


class StatusThread(threading.Thread):

    def __init__(self, bytes):
        threading.Thread.__init__(self)
        self.start_time = time.time()
        self.bytes = bytes

    def run(self):
        while True:
            time.sleep(10)
            now = time.time()
            elapsed_time = round(now - self.start_time)
            bytes_count = self.bytes.value
            print("Elapsed time: " + str(elapsed_time) + " seconds")
            print("Processed: " + str(bytes_count) + " bytes (" + str(bytes_count >> 30) + " Gi)")
            if elapsed_time % 60 == 0:
                print("\n------------------------\nKEYS:\n")
                print(unique_keys)
                # pprint.PrettyPrinter(indent=4).pprint(unique_keys)
                print("\n------------------------\n")


if __name__ == '__main__':
    jobs = Queue()
    bytes = Value("l", 0)  # 'i' = 'int'

    for i in range(1):
        t = ThreadClass(jobs, bytes)
        t.setDaemon(True)
        t.start()

    t = StatusThread(bytes)
    t.setDaemon(True)
    t.start()

    # Read file line by line
    if len(sys.argv) < 2:
        print("missing input file name")
        sys.exit()

    filename = sys.argv[1]
    input_stream = open(filename, "r")
    print("File (" + filename + ") have size: " + str(os.path.getsize(filename)) + " bytes\n")
    for line in input_stream:
        jobs.put(line)

    # wait on the queue until everything has been processed
    jobs.join()

    output_stream = open("output.txt", "w")
    output_stream.write(pprint.PrettyPrinter(indent=4).pformat(unique_keys))
    output_stream.close()
