__author__ = 'alan.lee'

from Queue import Queue
import threading
import socket
import select

BUFFER_SIZE = 4096
REQUEST_QUEUE_SIZE = 20
EPOLL_TIMEOUT = 15

CONNECTED = 1
DATA_AVAILABLE = 2
DISCONNECTED = 3


class Link:
    def __init__(self, socket_obj, connection):
        self._connection = connection
        self._socket = socket_obj
        self._read_buffer = bytearray()
        self._write_queue = Queue()

    def read(self):
        result = bytearray('')
        while True:
            read_count = self._connection.recv_into(self._read_buffer, BUFFER_SIZE)
            if read_count > 0:
                result.extend(self._read_buffer[:read_count - 1])
            else:
                break
        return bytearray

    def send(self, data):
        self._write_queue.put_nowait(data)
        self._socket.notify_send_data(self._connection.fileno())

    def write(self):
        while self._write_queue.not_empty():
            data = self._write_queue.get_nowait()
            self._connection.sendall(data)

    def close(self):
        self._connection.close()


class SocketServer(threading.Thread):
    def __init__(self, address, thread_pool, handler_factory):
        threading.Thread.__init__(name='SOCKET_SERVER')
        self._running = True
        self._thread_pool = thread_pool
        self._running = True
        self._handler_factory = handler_factory
        self._links = dict()
        self._is_shutdown = threading.Event()

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(address)

        self._epoll = select.epoll()

    def run(self):
        self._server_socket.listen(REQUEST_QUEUE_SIZE)
        self._server_socket.setblocking(False)

        self._epoll.register(self._server_socket, select.EPOLLIN)
        while self._running:
            events = self._epoll.poll(EPOLL_TIMEOUT)
            for fileno, event in events:
                if fileno == self._server_socket.fileno():
                    connection, address = self._server_socket.accept()
                    connection.setblocking(False)
                    self._epoll.register(connection.fileno(), select.EPOLLIN)

                    link = Link(self, connection)
                    self._links[fileno] = link

                    handler = self._handler_factory.get_handler(CONNECTED, link)
                    if handler is not None:
                        self._thread_pool.submit(handler)
                elif event & select.EPOLLIN:
                    link = self._links[fileno]
                    data = link.read()

                    handler = self._handler_factory.get_handler(DATA_AVAILABLE, link, data)
                    if handler is not None:
                        self._thread_pool.submit(handler)
                elif event & select.EPOLLOUT:
                    link = self._links[fileno]
                    link.write()
                    self._epoll.modify(fileno, select.EPOLLIN)
                elif event & select.EPOLLHUP:  # FIXME: is it EPOLLRDHUP?
                    self._epoll.unregister(fileno)
                    link = self._links[fileno]
                    link.close()

                    handler = self._handler_factory.get_handler(DISCONNECTED, link)
                    if handler is not None:
                        self._thread_pool.submit(handler)

                    del self._links[fileno]

    def shutdown(self):
        self._running = False
        self._is_shutdown.wait()

    def notify_send_data(self, fileno):
        if fileno in self._links:
            self._epoll.modify(fileno, select.EPOLLIN | select.EPOLLOUT)


class SocketClient(threading.Thread):
    def __init__(self, server_address, thread_pool, handler_factory):
        threading.Thread.__init__(name='SOCKET_CLIENT')
        self._running = True
        self._thread_pool = thread_pool
        self._running = True
        self._handler_factory = handler_factory
        self._link = None
        self._server_address = server_address
        self._is_shutdown = threading.Event()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._epoll = select.epoll()

    def run(self):
        self._socket.connect(self._server_address)
        self._socket.setblocking(False)
        self._link = Link(self, self._socket)

        self._epoll.register(self._socket, select.EPOLLIN)
        while self._running:
            events = self._epoll.poll(EPOLL_TIMEOUT)
            for fileno, event in events:
                if event & select.EPOLLIN:
                    data = self._link.read()

                    handler = self._handler_factory.get_handler(DATA_AVAILABLE, self._link, data)
                    if handler is not None:
                        self._thread_pool.submit(handler)
                elif event & select.EPOLLOUT:
                    self._links.write()
                    self._epoll.modify(fileno, select.EPOLLIN)
                elif event & select.EPOLLHUP:  # FIXME: is it EPOLLRDHUP?
                    self._epoll.unregister(fileno)
                    self._links.close()

                    handler = self._handler_factory.get_handler(DISCONNECTED, self._link)
                    if handler is not None:
                        self._thread_pool.submit(handler)

    def shutdown(self):
        self._running = False
        self._is_shutdown.wait()

    def notify_send_data(self, fileno):
        if fileno in self._links:
            self._epoll.modify(fileno, select.EPOLLIN | select.EPOLLOUT)