# MANDELBOT
"""
IRC network model.
Handles establishing a connection to, and interacting with, the IRC network.

Properties:
c (object)                 - the established connection to the IRC server
buffer (list)              - a list of messages waiting to be sent to the IRC network (prevents flooding)
messages (list)            - a list of messages received from the IRC network

config: name (str)         - the name of the network
        server (str)       - the address of the IRC network server
        port (int)         - the port the IRC server listens on
        ssl (bool)         - whether to connect using SSL or not
        autoconnect (bool) - whether to automatically connect to the IRC server when Mandelbot is launched
        username (str)     - used to identify Mandelbot with the IRC server
        password (str)     - used to identify Mandelbot with the IRC server
        realname (str)     - used to identify Mandelbot with the IRC server
        nickname (str)     - used to identify Mandelbot with the IRC server
        command (str)      - the command identifier Mandelbot listens for on this network
        owners (list)      - a list of IRC users who can administrate Mandelbot on this network
        users (list)       - a list of IRC users who can access Mandelbot's functions on this network
        chans (dict)       - a dictionary of the channels Mandelbot is connected to, along with the flags Mandelbot has on them

Methods :
connect                    - attempts to create a connection to the IRC server
identify                   - identifies Mandelbot with the IRC network
send                       - sends a message to the specified channel or user
receive                    - receives a message from the network and handles it
notice                     - sends a notice to the specified channel or user
join                       - joins a channel on the network
part                       - leaves a channel on the network
quit                       - leaves the IRC network and closes the connection to the server
"""

from . import connection, utils
from .exceptions import *

class network(object) :
    c = None
    delimiter = "\r\n"
    messages = []
    _read = False

    # This will be populated when the network is loaded from the configuration
    config = {"name": None,
              "server": None,
              "port": None,
              "autoconnect": None,
              "username": None,
              "password": None,
              "realname": None,
              "nickname": None,
              "flags": None,
              "command": None,
              "owners": None,
              "users": None,
              "chans": None}

    def connect(self) :
        try :
            self.c = connection.connection(self.config["server"], self.config["port"], False)
            self.c.connect()
            utils.console("Connection established ({})".format(self.name))
            self.c.handler = (self, "_parse")

        except InvalidConnectionInformation :
            raise InvalidServer

        except CouldNotConnect :
            raise NoServerConnection

    def identify(self) :
        try :
            utils.console("Identifying as {} on {}...".format(self.config["nickname"], self.config["name"]))
            self.send("NICK {}".format(self.config["nickname"]))
            self.send("USER {} * * :{}".format(self.config["username"], self.config["realname"]))

            if self.config["password"] :
                self.send("PRIVMSG NICKSERV : identify {} {}".format(self.config["username"], self.config["password"]))

            reply = self._wait()
            print("REPLY"+reply)

        except NoSocket :
            raise NoServerConnection



    def send(self, message) :
        message = message + self.delimiter
        self.c.send(message)

    def _wait(self, timeout = 10) :
        run = 0
        while (not self.read) and (run < timeout) :
            sleep(0.1)
            run += 1
        else :
            if self.read :
                return self._last()
            else :
                raise ReceiveTimeout

    def _receive(self, data) :
        self.messages.append(data)
        self._read = True

    def _last(self) :
        if self._read :
            self._read = False
            return self.messages.pop()
