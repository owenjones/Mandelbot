# MANDELBOT
"""
IRC network model.
Handles establishing a connection to, and interacting with, the IRC network.

TODO:
* Implement anti-flooding (buffer & time limit)

Properties:
c (object)                 - the established connection to the IRC server
delimiter (str)            - the character(s) that break up messages being sent to the network
buffer (list)              - a list of messages waiting to be sent to the IRC network (prevents flooding)
messages (list)            - a list of messages received from the IRC network
connected (bool)           - whether the network is connected or not

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
        limit (tuple)      - the limit of how many messages can be sent per second (messages, seconds)
        owner (str)        - the IRC user who can administrate Mandelbot on this network
        users (list)       - a list of IRC users who can access Mandelbot's protected functions on this network
        chans (dict)       - a dictionary of the channels Mandelbot is connected to, along with the modes Mandelbot has been granted on them

Methods:
connect                    - attempts to create a connection to the IRC server
identify                   - identifies Mandelbot with the IRC network
send                       - sends a message to the specified channel or user
notice                     - sends a notice to the specified channel or user
join                       - joins a channel on the network
part                       - leaves a channel on the network
quit                       - leaves the IRC network and closes the connection to the server

Internal Methods:
_receive                   - receives a message from the network and handles it
"""
from . import connection, utils
from .exceptions import *
import time

class network(object) :
    c = None
    delimiter = "\r\n"
    buffer = []
    messages = []
    connected = False
    config = {} # This will be populated when the network is loaded from the configuration

    def __init__(self, config) :
        self.config = config

    def connect(self) :
        try :
            self.c = connection.connection(self.config["host"], self.config["port"], self.config["ssl"], False)
            self.c.connect()
            self.connected = True
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
                #self.send("PRIVMSG NICKSERV : identify {} {}".format(self.config["username"], utils.password.decode(self.config["password"])))

            time.sleep(5)

            self.send("JOIN ##mandelbottesting")

        except NoSocket :
            raise NoServerConnection

    def quit(self, message = None) :
        q = "QUIT :{}".format(message) if message else "QUIT"
        self.send(q)

    def send(self, message) :
        message = message + self.delimiter
        print("SENDING: " + message)
        self.c.send(message)

    def _receive(self, data) :
        print("RECEIVED: {}".format(data))
        message = utils.message.parse(data, self.config["command"])

        if message["type"] == "PING" :
            self.send("PONG :{}".format(message["data"]))
