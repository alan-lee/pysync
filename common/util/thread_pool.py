__author__ = 'alan.lee'

from threading import Thread
from threading import Event
from threading import RLock
from Queue import Queue
from Queue import Empty


class Worker(Thread):
    def __init__(self, pool, task_queue, new_task_event, timeout=None):
        self._queue = task_queue
        self._pool = pool
        self._event = new_task_event
        self._running = True
        self._timeout = timeout

    def run(self):
        while self._running:
            if self._queue.empty():
                if not self._event.wait(self._timeout):
                    break
            try:
                task = self._queue.get_nowait()
                if callable(task):
                    task()
            except Empty:
                pass
        self._pool.remove_worker(self)

    def stop(self):
        self._running = False


class Shutdown:
    def __init__(self):
        pass


class ThreadPool:
    def __init__(self, core_thread, max_thread):
        self._THREAD_IDLE_TIME = 300  # if the thread idea more than 5 minutes, it will exit
        self._pool = list()
        self._pool_lock = RLock()
        self._task_queue = Queue()
        self._new_task_event = Event()
        self._core_thread_count = core_thread
        self._max_thread_count = max_thread
        self._shutdown = False

        for i in range(0, self._core_thread_count):
            worker = Worker(self, self._task_queue, self._new_task_event)
            worker.start()
            self._pool.append(worker)

    def submit(self, callee):
        if self._shutdown:
            raise Shutdown()
        self._task_queue.put(callee)
        self._new_task_event.set()

        self._pool_lock.acquire()
        if len(self._pool) < self._max_thread_count and (not self._task_queue.empty()):
            worker = Worker(self, self._task_queue, self._new_task_event, self._THREAD_IDLE_TIME)
            worker.start()
            self._pool.append(worker)
        self._pool_lock.release()

    def remove_worker(self, worker):
        self._pool_lock.acquire()
        self._pool.remove(worker)
        self._pool_lock.release()

    def shutdown(self):
        self._shutdown = True
        for worker in self._pool:
            worker.stop()

        self._new_task_event.set()