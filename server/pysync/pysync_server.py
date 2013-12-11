__author__ = 'alan.lee'

import sys
import os
import getopt
import atexit
import logging

LOG_FILE = '/var/log/pysync.log'
PID_FILE = '/var/run/pysync_server.pid'


class SyncServer:
    def __init__(self, daemon, directory, log_level = logging.ERROR):
        self._daemon = daemon
        self._directory = directory
        self._running = True

        self._logger = logging.getLogger()
        self._logger.setLevel(log_level)
        handler = logging.hanlders.RotatingFileHandler(LOG_FILE, maxBytes=4 * 1024 * 1024, backupCounts=10)
        self._logger.setHanlder(handler)

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
            os.remove(PID_FILE)
        except:
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


