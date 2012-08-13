import socket
import pickle
import random
import threading
import traceback
import select
import logging
import io

if not __name__ == "__main__":
    from .event import *
    from .endpoint import EndPoint

MIN_TCP_PORT = 10000
MAX_TCP_PORT = 20000
MAX_TCP_BUFSIZE = 2000          # Maximum pickled message size
MAX_RETRY = 5

class TcpEndPoint(EndPoint):
    senders = None
    receivers = None

    def __init__(self, name=None, host='localhost', port=None):
        super().__init__(name)

        self._log = logging.getLogger("runtime.TcpEndPoint")
        TcpEndPoint.receivers = dict()
        TcpEndPoint.senders = dict()

        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port is None:
            while True:
                self._address = (host,
                                 random.randint(MIN_TCP_PORT, MAX_TCP_PORT))
                try:
                    self._conn.bind(self._address)
                    break
                except socket.error:
                    pass
        else:
            self._address = (host, port)
            self._conn.bind(self._address)

        self._conn.listen(10)
        TcpEndPoint.receivers[self._conn] = self._address
        self._log.debug("TcpEndPoint %s initialization complete",
                        str(self._address))

    def send(self, data, src, timestamp = 0):
        retry = 1
        while True:
            conn = TcpEndPoint.senders.get(self)
            if conn is None:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    conn.connect(self._address)
                    TcpEndPoint.senders[self] = conn
                except socket.error:
                    self._log.warn("Can not connect to %s. Peer is down.",
                                   str(self._address))
                    return False

            bytedata = pickle.dumps((src, timestamp, data))

            if len(bytedata) > MAX_TCP_BUFSIZE:
                self._log.warn("Data size exceeded maximum buffer size! " +
                               "Outgoing packet dropped.")
                self._log.debug("Dropped packet: %s", str((src, timestamp, data)))
                break

            else:
                try:
                    if conn.send(bytedata) == len(bytedata):
                        break
                except socket.error as e:
                    pass

                self._log.warn("Error sending packet, retrying.")
                retry += 1
                if retry > MAX_RETRY:
                    self._log.debug("Max retry count reached, reconnecting.")
                    conn.close()
                    TcpEndPoint.senders[self] = None
                    retry = 1
        return True

    def recvmesgs(self):
        try:
            while True:
                r, _, _ = select.select(TcpEndPoint.receivers, [], [])

                if self._conn in r:
                    # We have pending new connections, handle those first
                    conn, addr = self._conn.accept()
                    TcpEndPoint.receivers[conn] = addr
                    r.remove(self._conn)
                    continue

                for c in r:
                    try:
                        bytedata = c.recv(MAX_TCP_BUFSIZE*10)
                        bio = io.BytesIO(bytedata)

                        while True:
                            try:
                                src, tstamp, data = pickle.load(bio)
                                if not isinstance(src, TcpEndPoint):
                                    raise TypeError()
                                else:
                                    yield (src, tstamp, data)

                            except EOFError:
                                break
                            except pickle.UnpicklingError as e:
                                self._log.warn(
                                    "UnpicklingError, packet from %s dropped",
                                    TcpEndPoint.receivers[c])
                                break
                        bio.close()

                    except socket.error as e:
                        self._log.warn("Remote connection %s terminated.", str(c))
                        TcpEndPoint.receivers.pop(c)

        except select.error as e:
            self._log.debug("select.error occured, terminating receive loop.")

    def __getstate__(self):
        return ("TCP", self._address, self._name)

    def __setstate__(self, value):
        proto, self._address, self._name = value
        self._conn = None
        self._log = logging.getLogger("runtime.TcpEndPoint")
