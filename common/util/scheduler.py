__author__ = 'alan.lee'

import time
import threading


class Timer:
    def __init__(self, interval, callee):
        self._interval = interval
        self._next = time.time() + self._interval
        if not callable(callee):
            raise BaseException("callee is not callable")

        self._callable = callee

    def next(self):
        self._next = time.time() + self._interval
        return self._next

    def get_next(self):
        return self._next

    def get_callable(self):
        return self._callable


class Scheduler(threading.Thread):
    def __init__(self, thread_pool):
        self._thread_pool = thread_pool
        self._event = threading.Event()
        self._timer_queue = list()
        self._queue_lock = threading.RLock()
        self._stopped = True
        self._next = None

    def add_timer(self, timer):
        self._queue_lock.acquire()
        self._timer_queue.append(timer)
        self._queue_lock.release()

        if not self._stopped:
            self._event.set()

    def run(self):
        self._stopped = False
        timeout = None
        while True:
            self._calc_next()
            if self._next is not None:
                # if self._next is NOne, the timeout will be None and
                # it will wait until new timer is appended to the queue
                timeout = self._next.get_next() - time.time()
            if timeout > 0 or timeout is None:
                self._event.wait(timeout)
            if self._stopped:
                break
            elif not self._event.isSet():
                # throw the callable into the thread pool
                self._thread_pool.submit(self._next.get_callable())
                self._next.next()

    def _calc_next(self):
        self._queue_lock.acquire()
        for timer in self._timer_queue:
            if self._next is None:
                self._next = timer
            elif self._next.get_next() > timer.get_next():
                self._next = timer
        self._queue_lock.release()

    def stop(self):
        self._stopped = True
        self._event.set()