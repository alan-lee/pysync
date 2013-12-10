__author__ = 'alan.lee'

import sys
import os
import getopt
import logging

LOG_FILE = '/var/log/pysync.log'


class SyncServer:
    def __init__(self, daemon, directory, log_level = logging.ERROR):
        self._daemon = daemon
        self._directory = directory
        self._running = True

        self._logger = logging.getLogger()
        self._logger.setLever(log_level)
        handler = logging.hanlders.RotatingFileHandler(LOG_FILE, maxBytes = 4 * 1024 * 1024, backupCounts = 10)
        self._logger.setHanlder(handler)

    def _daemonize(self):
        pass

    def serve_forever(self):
        if self._daemon:
            self._daemonize()

        while self._running:
            pass


def usage():
    pass


if __name__ == '__main__':
    opts, args = getopt.getoption(sys.argv[1:], 'hdl:D:', ['help', 'daemon', 'dir=', 'logging='])

    daemon = False
    directory = os.path.abspath(os.curdir)
    log_level = logging.ERROR
    for key, value in opts:
        if key in ('-h', '--help'):
            usage()
            exit(0)
        elif key in ('-d', '--daemon'):
            daemon = True
        elif key in ('-D', '--dir'):
            directory = value
        elif key in ('-l', '--logging'):
            log_level = int(value)
        else:
            print('*******Incorrect Arguments*********')
            usage()
            exit(-1)

    server = SyncServer(daemon, directory, log_level)
    server.serve_forever()


