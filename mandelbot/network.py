# MANDELBOT
"""
IRC network model.
Handles establishing a connection to, and interacting with, the IRC network.

TODO:
* Implement anti-flooding (buffer & time limit)

Properties:
bot (object)               - the current running instance of Mandelbot
connection (object)        - the established connection to the IRC server
parser (object)            - the message parser object for this network
state (object)             - the state object for this network
delimiter (str)            - the character(s) that break up messages being sent to the network
buff (list)                - a list of messages waiting to be sent to the IRC network (prevents flooding)
messages (list)            - a list of messages received from the IRC network
modes (list)               - the modes applied to the bot on this network

config: name (str)         - the name of the network
        host (str)         - the address of the IRC network server
        port (int)         - the port the IRC server listens on
        ssl (bool)         - whether to connect using SSL or not
        password (str)     - the password for the IRC server (if required)
        autoconnect (bool) - whether to automatically connect to the IRC server when Mandelbot is launched
        nickserv (str)     - the identification service on this network
        username (str)     - used to identify Mandelbot with the IRC server
        nickpass (str)     - used to identify Mandelbot with the IRC server
        realname (str)     - used to identify Mandelbot with the IRC server
        nickname (str)     - used to identify Mandelbot with the IRC server
        command (str)      - the command identifier Mandelbot listens for on this network
        owner (str)        - the IRC user who can administrate Mandelbot on this network
        users (list)       - a list of IRC users who can access Mandelbot's protected functions on this network
        chans (dict)       - a dictionary of the channels Mandelbot is connected to,
                             along with the modes Mandelbot has been granted on them

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
from . import connection, utils, parser
from .exceptions import *
import time

class network(object) :
    bot = None
    connection = None
    parser = None
    state = None
    delimiter = "\r\n"
    buff = []
    messages = []
    modes = []
    config = {} # This will be populated when the network is loaded from the configuration

    def __init__(self, config, bot) :
        self.bot = bot
        self.config = config
        self.parser = parser.parser(self)
        self.state = state()

    def connect(self) :
        try :
            self.connection = connection.connection(self.config["host"],
                                           self.config["port"],
                                           self.config["ssl"],
                                           False)
            self.connection.connect()
            utils.console("Connection established ({})".format(self.config["name"]))
            self.connection.handler = (self.parser, "parse")

            if self.config["password"] :
                self.send("PASS {}".format(utils.password.decode(self.config["password"])))

            self.send("USER {} * * :{}".format(self.config["username"], self.config["realname"]))
            self.send("NICK {}".format(self.config["nickname"]))

            self.testloop()

        except InvalidConnectionInformation :
            raise InvalidServer

        except CouldNotConnect :
            raise NoServerConnection

    def connected(self, params) :
        self.identify()
        self.state.connected()

    """
    Just for testing...
    """
    def testloop(self) :
        time.sleep(5)
        self.send("JOIN ##mandelbottesting")

    def nick(self, nick) :
        self.send("NICK :{}".format(nick))

    def identify(self) :
        if self.config["nickpass"] :
            utils.console("Identifying as {} on {}".format(self.config["nickname"],
                                                              self.config["name"]))

            self.send("PRIVMSG {} :identify {} {}".format(self.config["nickserv"],
                                                          self.config["nickname"],
                                                          utils.password.decode(self.config["nickpass"])))

            self.nick(self.config["nickname"])

    def message(self, target, message) :
        self.send("PRIVMSG {} :{}".format(target, message))

    def notice(self, target, message) :
        self.send("NOTICE {} :{}".format(target, message))

    def nickchanged(self, returned) :
        self.config["nickname"] = returned[1:]

    def modechanged(self, modes) :
        pass

    def pong(self, host) :
        self.send("PONG :{}".format(host[1:]))

    def shutdown(self, returned) :
        self.bot.shutdown(returned["data"])

    def quit(self, message = None) :
        q = "QUIT :{}".format(message[0]) if message[0] else "QUIT"
        self.send(q)
        self.connection.close(True)

    def send(self, message) :
        message = message + self.delimiter
        self.connection.send(message)

"""
Network States
"""
class state(object) :
    isConnected = False
    isWelcome = False
    isIdentified = False
    isActive = False

    def connected(self) :
        self.isConnected = True

    def welcome(self) :
        self.isWelcome = True

    def identified(self) :
        self.isIdentified = True

    def active(self) :
        self.isActive = True