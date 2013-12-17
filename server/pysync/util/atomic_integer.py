__author__ = 'alan.lee'

from threading import RLock


class AtomicInteger:
    def __init__(self, val=0):
        self._val = val
        self._lock = RLock()

    def inc(self):
        self.add(1)

    def dec(self):
        self.sub(1)

    def get(self):
        self._lock.acquire()
        val = self._val
        self._lock.release()
        return val

    def set(self, val):
        self._lock.acquire()
        self._val = val
        self._lock.release()

    def add(self, i):
        self._lock.acquire()
        self._val += i
        val = self._val
        self._lock.release()
        return val

    def sub(self, i):
        self._lock.acquire()
        self._val -= i
        val = self._val
        self._lock.release()
        return val

    def compare(self, i):
        self._lock.acquire()
        result = self._val - i
        self._lock.release()
        return result