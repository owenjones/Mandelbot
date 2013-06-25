# MANDELBOT
"""
IRC network model.
Handles establishing a connection to, and interacting with, the IRC network.

Properties:
c (object)                 - the established connection to the IRC server
buffer (list)              - a list of messages waiting to be sent to the IRC network (prevents flooding)
messages (list)            - a list of messages received from the IRC network

config: name (str)         - the name of the network
        host (str)         - the address of the IRC network server
        port (int)         - the port the IRC server listens on
        ssl (bool)         - whether to connect using SSL or not
        autoconnect (bool) - whether to automatically connect to the IRC server when Mandelbot is launched
        username (str)     - used to identify Mandelbot with the IRC server
        password (str)     - used to identify Mandelbot with the IRC server
        realname (str)     - used to identify Mandelbot with the IRC server
        nickname (str)     - used to identify Mandelbot with the IRC server
        command (str)      - the command identifier Mandelbot listens for on this network
        owner (str)        - the IRC user who can administrate Mandelbot on this network
        users (list)       - a list of IRC users who can access Mandelbot's protected functions on this network
        chans (dict)       - a dictionary of the channels Mandelbot is connected to, along with the modes Mandelbot has been granted on them

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
import base64
from . import connection, utils
from .exceptions import *

class network(object) :
    c = None
    delimiter = "\r\n"
    messages = []
    config = {} # This will be populated when the network is loaded from the configuration

    def __init__(self, config) :
        self.config = config

    def connect(self) :
        try :
            self.c = connection.connection(self.config["host"], self.config["port"], self.config["ssl"], False)
            self.c.connect()
            utils.console("Connection established ({})".format(self.config["name"]))
            self.c.handler = (self, "_receive")

            self.identify()

        except InvalidConnectionInformation :
            raise InvalidServer

        except CouldNotConnect :
            raise NoServerConnection

    def identify(self) :
        try :
            utils.console("Identifying as {} on {}...".format(self.config["nickname"], self.config["name"]))
            self.send("NICK {}".format(self.config["nickname"]))
            self.send("USER {} * * :{}".format(self.config["username"], self.config["realname"]))

            #if self.config["password"] :
            #    password = base64.b64decode(self.config["password"])
            #    self.send("PRIVMSG NICKSERV : identify {} {}".format(self.config["username"], password))

        except NoSocket :
            raise NoServerConnection

    def send(self, message) :
        message = message + self.delimiter
        print("SENDING: " + message)
        self.c.send(message)

    def _receive(self, data) :
        print("RECEIVING: " + data)
        self.messages.append(data)
