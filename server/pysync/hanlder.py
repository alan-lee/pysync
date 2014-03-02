__author__ = 'alan.lee'

from common.network import CONNECTED
from common.network import DATA_AVAILABLE
from common.network import DISCONNECTED
from common import Packet


class HandlerFactory:
    def __init__(self):
        pass

    @classmethod
    def create_handler(cls, event_type, link, data=None):
        if event_type == CONNECTED:
            return ConnectedHandler(link)
        elif event_type == DATA_AVAILABLE:
            return DataAvailableHandler(link, data)
        elif event_type == DISCONNECTED:
            return DisconnectedHandler(link)
        else:
            return None


class ConnectedHandler:
    def __init__(self, link):
        self._link = link

    def __call__(self, *args, **kwargs):
        pass


class DataAvailableHandler:
    def __init__(self, link, data):
        self._link = link
        self._data = data

    def __call__(self, *args, **kwargs):
        packet = Packet(self._data)

        pass  # TODO: get the frame and dispatch the request


class DisconnectedHandler:
    def __init__(self, link):
        self._link = link

    def __call__(self, *args, **kwargs):
        pass


class DirMonitorHandler:
    def __init__(self, monitor):
        self._monitor = monitor

    def __call__(self, *args, **kwargs):
        counter = self._monitor.get_and_clear_counter()
        if counter > 0:
            pass  # TODO: rebuild the hash_tree
