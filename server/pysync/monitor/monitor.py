__author__ = 'alan.lee'

import threading

import pyinotify

from common import AtomicInteger


class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, monitor):
        self._monitor = monitor

    def process_IN_CREATE(self, event):
        self._monitor.inc_counter()

    def process_IN_DELETE(self, event):
        self._monitor.inc_counter()

    def process_IN_MODIFY(self, event):
        self._monitor.inc_counter()


class Monitor(threading.Thread):
    def __init__(self, dir_path):
        threading.Thread.__init__(name='DIR_MONITOR')
        self._dir = dir_path
        self._running = True

        self._wm = pyinotify.WatchManager()
        self._handler = EventHandler(self)
        self._notifier = pyinotify.Notifier(self._wm, self._handler)

        self._counter = AtomicInteger()
        self._wd = {}

    def run(self):
        self._wd = self._wm.add_watch(self._dir, pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MODIFY,
                                      rec=True, auto_add=True)

        while self._running:
            self._notifier.process_events()
            if self._notifier.check_events():
                self._notifier.read_events()

    def stop(self):
        self._running = False
        self._notifier.stop()
        self._wm.rm_watch(self._wd[self._dir])

    def inc_counter(self):
        self._counter.inc()

    def clear_counter(self):
        self._counter.set(0)

    def get_and_clear_counter(self):
        return self._counter.exchange(0)
