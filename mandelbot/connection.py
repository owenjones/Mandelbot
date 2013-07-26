# Mandelbot
"""
Provides methods for initiating a connection and sending/receiving messages at the socket level.

Properties:
sock (socket)              - the created socket
thread (thread)            - the thread that checks if data can be sent and received
server (str)               - the server to connect to
port (int)                 - the port to connect to on the server
ssl (bool)                 - whether to initiate an SSL connection or not
blocking (bool)            - whether the socket should be blocking or not
handler (tuple, list)      - the handler that received responses should be passed to
                           - defined as (namespace, method); must take a single string argument
delimiter (str)            - the delimiter for data received by from the socket,
                             received messages are split according to this

Internal Properties:
_buffer (list)             - contains the messages that are waiting to be sent to the socket
_closing (bool)             - triggered when the socket is preparing to close
"""
import socket, ssl, select, time, threading
from mandelbot import utils
from mandelbot.exceptions import *

class connection(object) :
    sock = None
    thread = None
    server = None
    port = None
    ssl = None
    blocking = None
    handler = "_output"
    delimiter = "\n"

    _buffer = []
    _closing = False

    def __init__(self, server, port = 80, usessl = False, blocking = True) :
        """Creates a new socket"""
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
        """Initiates a connection to the socket and launches the checking thread"""
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
        """Ends the socket connection (finishes sending message
        buffer first if graceful is specified)"""
        try :
            assert isinstance(self.sock, socket.socket)

            if graceful and not self._closing :
                self._closing = True

            else :
                self.sock.shutdown(socket.SHUT_WR)
                self.sock.close()

                if not self.blocking :
                    self.thread.stop()

        except AssertionError :
            raise NoSocket

        except socket.error as e :
            raise CouldNotDisconnect(str(e))

    def send(self, data) :
        """Adds a message to the outgoing message buffer"""
        try :
            assert isinstance(self.sock, socket.socket)
            self._buffer.append(data)

        except AssertionError :
            raise NoSocket

    def _register(self) :
        """Creates a thread that handles checking if data can be sent and received
        (and then calls _send and _receive)"""
        try :
            assert isinstance(self.sock, socket.socket)
            self.thread = _SocketConditions(self)
            self.thread.start()

        except AssertionError :
            raise NoSocket

    def _send(self) :
        """Runs through the message buffer and sends messages to the socket"""
        try :
            if self._closing and not self._buffer :
                self.close()

            elif self._buffer :
                for data in self._buffer :
                    data = data.encode("UTF-8")
                    self.sock.send(data)

                self._buffer = []

        except socket.error as e :
            raise CouldNotSend(str(e))

    def _receive(self) :
        """Accepts data from the socket and splits it into messages,
        then hands these off to the response handler"""
        try :
            message = ""

            data = self.sock.recv(4096)

            if self.blocking and not data :
                raise SocketClosedUnexpectedly

            try :
                data = data.decode("UTF-8")

            except UnicodeDecodeError :
                data = data.decode("UTF-16")

            for part in data:
                message += part

                if part == self.delimiter :
                    self._handle(message)
                    message = ""

        except socket.error as e :
            raise CouldNotReceive(str(e))

    def _handle(self, message) :
        """Passes the message on to the handler"""
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
        """Default handler, just prints the response to the console"""
        message = message[:-1]
        utils.log().info(message)

"""
_SocketConditions - Launches a thread that repeatedly checks if the socket is ready to send or receive data
                    then launches the _send and _receive methods as appropriate
"""
class _SocketConditions(threading.Thread) :
    conn = None
    sock = None

    def __init__(self, conn) :
        threading.Thread.__init__(self)
        self.conn = conn
        self.sock = self.conn.sock

    def run(self) :
        try :
            while self.sock :
                read, write, error = select.select([self.sock], [self.sock], [], 0)

                if read :
                    self.conn._receive()

                if write :
                    self.conn._send()

                time.sleep(0.1)

            else :
                return

        except (TimeoutError, socket.timeout) :
            # Timeouts are handled by the network, being passed timeoutexceptions
            # from here just complicates things.
            pass

    def stop(self) :
        self.sock = False
