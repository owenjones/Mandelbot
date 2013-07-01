# MANDELBOT
"""
Provides methods for initiating a connection and sending/receiving messages at the socket level.

Properties:
sock (socket)              - the created socket
thread (thread)            - the thread that checks if data can be sent and received
server (str)               - the server to connect to
port (int)                 - the port to connect to on the server
ssl (bool)                 - whether to initiate an SSL connection or not
blocking (bool)            - whether the socket should be blocking or not
closing (bool)             - triggered when the socket is preparing to close
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
    thread = None
    server = None
    port = None
    ssl = None
    blocking = None
    closing = False
    handler = "_output"
    delimiter = "\n"
    _buffer = []

    def __init__(self, server, port = 80, usessl = False, blocking = True) :
        try :
            assert isinstance(server, str)
            assert isinstance(port, int)
            assert isinstance(usessl, bool)
            assert isinstance(blocking, bool)

            self.server = server
            self.port = port
            self.ssl = usessl
            self.blocking = blocking

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self.ssl :
                self.sock = ssl.wrap_socket(sock)
            else :
                self.sock = sock

        except AssertionError :
            raise InvalidConnectionInformation

    def connect(self) :
        try :
            assert isinstance(self.sock, socket.socket)
            self.sock.connect((self.server, self.port))
            self.sock.setblocking(self.blocking)

            if not self.blocking :
                self._register()

        except AssertionError :
            raise NoSocket

        except socket.error as e :
            raise CouldNotConnect(str(e))

    def close(self, graceful = False) :
        try :
            assert isinstance(self.sock, socket.socket)

            if graceful and not self.closing :
                self.closing = True

            else :
                self.sock.shutdown(socket.SHUT_WR)
                self.sock.close()
                self.thread.stop()

        except AssertionError :
            raise NoSocket

        except socket.error as e :
            raise CouldNotDisconnect(str(e))

    def send(self, data) :
        try :
            assert isinstance(self.sock, socket.socket)
            self._buffer.append(data)

        except AssertionError :
            raise NoSocket

    def _register(self) :
        try :
            assert isinstance(self.sock, socket.socket)
            self.thread = _SocketConditions(self)
            self.thread.start()

        except AssertionError :
            raise NoSocket

    def _send(self) :
        try :
            if self.closing and not self._buffer :
                self.close()

            for data in self._buffer :
                data = data.encode("UTF-8")
                self.sock.send(data)

            self._buffer = []

        except socket.error as e :
            raise CouldNotSend(str(e))

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
            raise CouldNotReceive(str(e))

    def _handle(self, message) :
        try :
            assert isinstance(self.handler, (str, tuple, list))

            if isinstance(self.handler, str) :
                namespace = self
                method = self.handler

            elif isinstance(self.handler, (tuple, list))  :
                namespace = self.handler[0]
                method = self.handler[1]

            getattr(namespace, method)(message)

        except (AssertionError, AttributeError) :
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
            read, write, error = select.select([self.sock], [self.sock], [], 0)

            if read :
                self.conn._receive()

            if write :
                self.conn._send()

            time.sleep(0.1)

    def stop(self) :
        self.sock = False
