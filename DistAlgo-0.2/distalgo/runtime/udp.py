import socket
import pickle
import random
import logging

if not __name__ == "__main__":
    from .event import *
    from .endpoint import EndPoint

MIN_UDP_PORT = 10000
MAX_UDP_PORT = 20000
MAX_UDP_BUFSIZE = 200000

class UdpEndPoint(EndPoint):
    sender = None

    def __init__(self, name=None, host='localhost', port=None):
        super().__init__(name)

        self._log = logging.getLogger("runtime.UdpEndPoint")
        UdpEndPoint.sender = None

        self._conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if port is None:
            while True:
                self._address = (host,
                                 random.randint(MIN_UDP_PORT, MAX_UDP_PORT))
                try:
                    self._conn.bind(self._address)
                    break
                except socket.error:
                    pass
        else:
            self._address = (host, port)
            self._conn.bind(self._address)

        self._log.debug("UdpEndPoint %s initialization complete",
                        str(self._address))


    def send(self, data, src, timestamp = 0):
        if UdpEndPoint.sender is None:
            UdpEndPoint.sender = socket.socket(socket.AF_INET,
                                               socket.SOCK_DGRAM)

        bytedata = pickle.dumps((src, timestamp, data))
        if len(bytedata) > MAX_UDP_BUFSIZE:
            self._log.warn("Data size exceeded maximum buffer size!" +
                           " Outgoing packet dropped.")
            self._log.debug("Dropped packet: %s", str((src, timestamp, data)))

        elif UdpEndPoint.sender.sendto(bytedata, self._address) != len(bytedata):
            raise socket.error()

    def recvmesgs(self):
        flags = 0

        try:
            while True:
                bytedata = self._conn.recv(MAX_UDP_BUFSIZE, flags)
                src, tstamp, data = pickle.loads(bytedata)
                if not isinstance(src, UdpEndPoint):
                    raise TypeError()
                else:
                    yield (src, tstamp, data)
        except socket.error as e:
            self._log.debug("socket.error occured, terminating receive loop.")

    def __getstate__(self):
        return ("UDP", self._address, self._name)

    def __setstate__(self, value):
        proto, self._address, self._name = value
        self._conn = None
        self._log = logging.getLogger("runtime.UdpEndPoint")
