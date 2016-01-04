#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os,time,platform,sys
import hashlib
import re
import urllib
reload(sys)

system_information=platform.platform()
sys.setdefaultencoding('utf8')

import os
import threading
import multiprocessing

# worker function
def worker(sign, lock):
    lock.acquire()
    print(sign, os.getpid())
    lock.release()

# Main
print('Main:',os.getpid())

# Multi-thread
# record = []
# lock  = threading.Lock()
# for i in range(5):
#     thread = threading.Thread(target=worker,args=('thread',lock))
#     thread.start()
#     record.append(thread)

# for thread in record:
#     thread.join()


record = []
lock = multiprocessing.Lock()
for i in range(5):
    process = multiprocessing.Process(target=worker,args=('process',lock))
    process.start()
    record.append(process)

for process in record:
    process.join()

