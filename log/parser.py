#!/usr/bin/env python3

import sys, os
from urllib.request import urlopen

import ijson
import json

import time
import multiprocessing.pool as mp
import _thread
import threading
from queue import Queue

"""
Because we’re assuming that the JSON file won’t fit in memory, 
we can’t just directly read it in using the json library. 
Instead, we’ll need to iteratively read it in in a memory-efficient way.
"""

unique_keys = set()
# output_stream = open("output.txt", "w")
# job queue
queue = Queue()


def process_new_line(input):
    print(_thread.get_ident())
    j = json.loads(line)
    for k in j.keys():
        unique_keys.add(k)


class ThreadClass(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get from queue job
            line = self.queue.get()
            process_new_line(line)
            # signals to queue job is done
            self.queue.task_done()


if __name__ == '__main__':
    # thread_pool.apply_async(process_new_line, args=(input_straem))
    # # output_stream.close()
    #
    # thread_pool.join()
    # print(unique_keys)

    start = time.time()

    # Create number process
    for i in range(8):
        t = ThreadClass(queue)
        t.setDaemon(True)
        # Start thread
        t.start()

    # Read file line by line
    if len(sys.argv) < 2:
        print("missing input file name")
        sys.exit()
    input_stream = open(sys.argv[1], "r")
    for line in input_stream:
        queue.put(line)

    # wait on the queue until everything has been processed
    queue.join()
    print(unique_keys)
    end = time.time()
    print("Elapsed time: " + str(end - start))
