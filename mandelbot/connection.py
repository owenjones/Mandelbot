# MANDELBOT
"""
Provides methods for initiating a connection and sending/receiving messages at the socket level.

Properties:
sock (socket)              - the created socket
server (str)               - the server to connect to
port (int)                 - the port to connect to on the server
ssl (bool)                 - whether to initiate an SSL connection or not
blocking (bool)            - whether the socket should be blocking or not
handler (tuple, list)      - the handler that received responses should be passed to
                           - defined as (namespace, method); must take a single string argument
delimiter (str)            - the delimiter for data received by from the socket, received messages are split according to this

Internal Properties:
_buffer (list)             - contains the messages that are waiting to be sent to the socket

Methods:
__init__  (str,int,bool)   - creates a socket
connect                    - initiates a connection to the socket and launches the checking thread
close                      - ends the socket connection
send (str)                 - adds a message to the outgoing message buffer

Internal Methods:
_register                  - creates a thread that handles checking if data can be sent and received (and then calls _send and _receive)
_send                      - runs through the message buffer and sends messages to the socket
_receive                   - accepts data from the socket and splits it into messages, then hands these off to the response handler
_handle (str)              - passes the message on to the handler
_output (str)              - default handler, just prints the response to the console
"""
import socket, ssl, select, time
from threading import Thread
from . import utils
from .exceptions import (InvalidConnectionInformation, InvalidHandler, NoSocket,
                         CouldNotConnect, CouldNotDisconnect, CouldNotSend,
                          CouldNotReceive, SocketClosedUnexpectedly)

class connection(object) :
    sock = None
    server = None
    port = None
    ssl = None
    blocking = None
    handler = "_output"
    delimiter = "\n"
    _buffer = []

    def __init__(self, server, port = 80, usessl = False, blocking = True) :
        try :
            assert isinstance(server, str)
            assert isinstance(port, int)
            assert isinstance(usessl, bool)
            assert isinstance(blocking, bool)

        except AssertionError :
            raise InvalidConnectionInformation

        self.server = server
        self.port = port
        self.ssl = usessl
        self.blocking = blocking

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.ssl :
            self.sock = ssl.wrap_socket(sock)
        else :
            self.sock = sock


    def connect(self) :
        try :
            assert isinstance(self.sock, socket.socket)

        except AssertionError :
            raise NoSocket

        try :
            self.sock.connect((self.server, self.port))
            self.sock.setblocking(self.blocking)

            if not self.blocking :
                self._register()

        except socket.error as e :
            raise CouldNotConnect(e.strerror, e.errno)

    def close(self) :
        try :
            assert isinstance(self.sock, socket.socket)

        except AssertionError :
            raise NoSocket

        try :
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()

        except socket.error as e :
            raise CouldNotDisconnect(e.strerror, e.errno)

    def send(self, data) :
        try :
            assert isinstance(self.sock, socket.socket)

        except AssertionError :
            raise NoSocket

        self._buffer.append(data)

    def _register(self) :
        try :
            assert isinstance(self.sock, socket.socket)

        except AssertionError :
            raise NoSocket

        t = _SocketConditions(self)
        t.start()

    def _send(self) :
        try :
            for data in self._buffer :
                data = data.encode("UTF-8")
                self.sock.send(data)

            self._buffer = []

        except socket.error as e :
            raise CouldNotSend(e.strerror, e.errno)

    def _receive(self) :
        try :
            message = ""

            data = self.sock.recv(4096)

            try :
                data = data.decode("UTF-8")

            except UnicodeDecodeError :
                data = data.decode("UTF-16")

            if self.blocking and not data :
                raise SocketClosedUnexpectedly

            for part in data:
                message += part

                if part == self.delimiter :
                    self._handle(message)
                    message = ""

        except socket.error as e :
            raise CouldNotReceive(e.strerror, e.errno)

    def _handle(self, message) :
        try :
            assert isinstance(self.handler, (str, tuple, list))

        except AssertionError :
            raise InvalidHandler

        if isinstance(self.handler, str) :
            namespace = self
            method = self.handler

        elif isinstance(self.handler, (tuple, list))  :
            namespace = self.handler[0]
            method = self.handler[1]

        try :
            getattr(namespace, method)(message)

        except :
            raise InvalidHandler

    def _output(self, message) :
        message = message[:-1]
        utils.console(message)

"""
_SocketConditions - Launches a thread that repeatedly checks if the socket is ready to send or receive data
                    then launches the _send and _receive methods as appropriate
"""
class _SocketConditions(Thread) :
    conn = None
    sock = None

    def __init__(self, conn) :
        Thread.__init__(self)
        self.conn = conn
        self.sock = self.conn.sock

    def run(self) :
        while self.sock :
            try :
                read, write, error = select.select([self.sock], [self.sock], [], 0)

                if read :
                    self.conn._receive()

                if write :
                    self.conn._send()

                time.sleep(0.1)

            except :
                self.conn.close()
                self.sock = False
                raise SocketClosedUnexpectedly
