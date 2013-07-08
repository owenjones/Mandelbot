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
        chans (dict)       - a dictionary of the channels Mandelbot is to join,
                             and the key (if required)

Methods:
connect                    - attempts to create a connection to the IRC server
identify                   - identifies Mandelbot with the IRC network
send                       - sends a message to the specified channel or user
notice                     - sends a notice to the specified channel or user
join                       - joins a channel on the network
part                       - leaves a channel on the network
quit                       - leaves the IRC network and closes the connection to the server
"""
from . import connection, utils, parser, channel, decorators
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
    channels = {}
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
            self.nick()

        except InvalidConnectionInformation :
            raise InvalidServer

        except CouldNotConnect :
            raise NoServerConnection

    def send(self, message) :
        message = message + self.delimiter
        self.connection.send(message)

    def join(self, chan, key) :
        self.channels[chan] = channel.channel(self, chan, key)
        self.channels[chan].join()

    def joinChannels(self) :
        for chan in self.config["chans"] :
            self.join(chan["name"], chan["key"])

    def quit(self, message) :
        q = "QUIT :{}".format(message) if message else "QUIT"
        self.send(q)
        self.connection.close(True)

    def shutdown(self, message) :
        self.bot.shutdown(message)

    # Nickname Managment
    def nick(self, nick = None) :
        nick = nick if nick else self.config["nickname"]
        self.send("NICK :{}".format(nick))

    def identify(self, params = None) :
        if self.config["nickpass"] :
            utils.console("Identifying as {} on {}...".format(self.config["nickname"],
                                                              self.config["name"]))

            self.send("PRIVMSG {} :identify {} {}".format(self.config["nickserv"],
                                                          self.config["nickname"],
                                                          utils.password.decode(self.config["nickpass"])))

            self.nick()

    # General Message Types
    def pong(self, host) :
        self.send("PONG :{}".format(host[1:]))

    def message(self, target, message) :
        self.send("PRIVMSG {} :{}".format(target, message))

    def notice(self, target, message) :
        self.send("NOTICE {} :{}".format(target, message))

    # Network Events
    def connected(self, params) :
        self.identify()
        self.state.connected()

    def nickchanged(self, returned) :
        self.config["nickname"] = returned[1:]

    def modechanged(self, params) :
        if params[2] == self.config["nickname"] :
            modes = params[3]
            action = "append" if modes[0] == "+" else "remove"

            for m in modes[1:] :
                if m == "r" and action == "append" :
                    utils.console("...identified")
                    self.state.identified()
                    self.joinChannels()

                getattr(self.modes, action)(m)

    def joined(self, params) :
        utils.console("{} joined {}".format(self.config["nickname"], params[1]))
        self.channels[params[1]].joined()

    def kicked(self, params) :
        utils.console("{} kicked from {} on {}".format(self.config["nickname"], params[2]))
        self.channels[params[2]].join()

    # Basic Mandelbot Commands
    @decorators.owner
    def cmd_quit(self, flags) :
        self.quit(flags[0])

    @decorators.owner
    def cmd_shutdown(self, flags) :
        self.shutdown(flags[0])

    @decorators.user
    def cmd_join(self, flags) :
        parts = flags[0].split(" ", 1)
        chan = parts[0]
        key = parts[1] if len(parts) > 1 else False

        self.join(chan, key)

    @decorators.user
    def cmd_part(self, flags) :
        self.channels[flags[1][2]].part(flags[0])

    @decorators.user
    def cmd_callbacks(self, flags) :
        self.message(flags[1][2], "Callbacks: {}".format(self.parser.callback))

    @decorators.user
    def cmd_builtins(self, flags) :
        self.message(flags[1][2], "Builtins: {}".format(self.parser.builtin))

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
