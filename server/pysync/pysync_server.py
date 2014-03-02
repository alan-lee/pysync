__author__ = 'alan.lee'

import sys
import os
import getopt
import atexit
import logging
import threading
from hanlder import HandlerFactory, DirMonitorHandler
from common import ThreadPool, Scheduler, Timer
from monitor import Monitor
from common import SocketServer

LOG_FILE = '/var/log/pysync.log'
PID_FILE = '/var/run/pysync_server.pid'
CORE_THREAD_COUNT = 4
MAX_THREAD_COUNT = 10
DIR_MONITOR_INTERVAL = 1800
SERVER_SOCKET_PORT = 7199


class SyncServer:
    def __init__(self, daemon, directory, log_level = logging.ERROR):
        self._daemon = daemon
        self._directory = directory
        self._handler_factory = HandlerFactory()
        self._server_socket = None
        self._is_shutdown = threading.Event()
        self._running = True

        self._logger = logging.getLogger()
        self._logger.setLevel(log_level)
        handler = logging.hanlders.RotatingFileHandler(LOG_FILE, maxBytes=4 * 1024 * 1024, backupCounts=10)
        self._logger.setHanlder(handler)

        self._thread_pool = ThreadPool(CORE_THREAD_COUNT, MAX_THREAD_COUNT)
        self._monitor = Monitor(directory)
        self._scheduler = Scheduler(self._thread_pool)
        self._socket_server = SocketServer(('0.0.0.0', SERVER_SOCKET_PORT), self._thread_pool, HanlderFactory())

    def _daemonize(self):
        try:
            #the first fork
            pid = os.fork()
            if pid > 0:
                #parent process, exit
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('fork #1 failed: %d(%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        #decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        #the second fork
        try:
            pid = os.fork()
            if pid > 0:
                #second parent process, exit
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('fork #2 failed: %d(%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        #redirect the standard io file descriptor
        sys.stdout.flush()
        sys.stderr.flush()

        redirect_in = file('/dev/null', 'r')
        redirect_out = file('/dev/null', 'a+')
        redirect_err = file('/dev/null', 'a+', 0)
        os.dup2(redirect_in, sys.stdin.fileno())
        os.dup2(redirect_out, sys.stdout.fileno())
        os.dup2(redirect_err, sys.stderr.fileno())

        pid = os.getpid()
        pid_file = file(PID_FILE, 'w+')
        pid_file.write('%d\n' % pid)
        pid_file.close()

        atexit.register(self._exit())

    def _exit(self):
        try:
            # TODO: stop all the components
            os.remove(PID_FILE)
        except:
            pass

    def serve_forever(self):
        if self._daemon:
            self._daemonize()

        self._monitor.start()
        self._scheduler.add_timer(Timer(DIR_MONITOR_INTERVAL, DirMonitorHandler()))
        self._scheduler.start()
        self._socket_server.start()


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


