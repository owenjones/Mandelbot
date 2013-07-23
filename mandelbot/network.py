# MANDELBOT
"""
IRC network model.
Handles establishing a connection to, and interacting with, the IRC network.

TODO:
* Implement anti-flooding (buffer & time limit)
* Separate basic commands from network model
"""
from mandelbot import utils, connection, channel
from mandelbot.exceptions import *

"""
Network States
"""
class state(object) :
    isConnected = False
    isWelcome = False
    isIdentified = False

    def connected(self) :
        self.isConnected = True

    def welcome(self) :
        self.isWelcome = True

    def identified(self) :
        self.isIdentified = True

class network(state) :
    bot = None
    connection = None
    delimiter = "\r\n"
    buff = []
    messages = []
    modes = []
    channels = {}
    config = {}

    events = {"PING"    : "_pong",
              "001"     : "_connected",
              "JOIN"    : "_joined",
              "NICK"    : "_nick",
              "MODE"    : "_mode",
              "KICK"    : "_kicked",
              "NOTICE"  : "_message",
              "PRIVMSG" : "_message"}

    def __init__(self, config, bot) :
        self.bot = bot
        self.config = config

    def event(self, call, params) :
        """Triggers the handler for the network event"""
        try :
            call = self.events[call]

        except KeyError :
            return

        try :
            getattr(self, call)(params)

        except Exception as e :
            utils.log().error("Error with builtin: [{}]".format(e))

    def connect(self) :
        """Connects to the IRC network"""
        try :
            self.connection = connection.connection(self.config["host"],
                                                    self.config["port"],
                                                    self.config["ssl"],
                                                    False)

            self.connection.connect()
            self.connection.handler = (self, "parse")

            if self.config["password"] :
                self.send("PASS {}".format(utils.password.decode(self.config["password"])))

            self.send("USER {} * * :{}".format(self.config["username"], self.config["realname"]))
            self.nick()

        except InvalidConnectionInformation :
            utils.log().error("Connection information for network \"{}\" is invalid.".format(self.config["name"]))

        except CouldNotConnect :
            utils.log().error("Could not connect to network \"{}\".".format(self.config["name"]))

    def parse(self, raw) :
        """Parses a received message from the network"""
        raw = raw.strip()
        utils.log().debug("Received: {}".format(raw))
        parts = raw.split(" ", 3)
        if parts[0] == "PING" :
            self.event("PING", parts[1])

        elif parts[1] in ("JOIN", "NICK", "PART") :
            addr = utils.host(parts[0])
            msg = parts[2][1:] if parts[2][0] == ":" else parts[2]
            self.event(parts[1], (addr, msg))

        else :
            addr, cmd, tgt, msg = parts
            addr = utils.host(addr)

            if tgt[0] != "#" :
                tgt = self.config["nickname"] if cmd == "MODE" else addr.nick

            msg = msg[1:] if msg[0] is ":" else msg

            self.event(cmd, (addr, cmd, tgt, msg))

    def send(self, message) :
        """Sends a message to the network"""
        utils.log().debug("Sent: {}".format(message))
        message = message + self.delimiter
        self.connection.send(message)

    def join(self, chan, key = False) :
        """Joins a channel on the network"""
        chan = chan.lower()
        self.channels[chan] = channel.channel(self, chan, key)
        self.channels[chan].join()

    def joinChannels(self) :
        """Joins the channels saved in the network configuration"""
        for chan in self.config["chans"] :
            self.join(chan["name"], chan["key"])

    def quit(self, message = False) :
        """Gracefully closes the connection to this network"""
        q = "QUIT :{}".format(message) if message else "QUIT"
        self.send(q)
        self.connection.close(True)

    def shutdown(self, message) :
        """Gracefully closes the connection to all networks, and halts the bot"""
        bot.shutdown(message)

    # Nickname Managment
    def nick(self, nick = None) :
        """Changes the bots nickname on the network"""
        nick = nick if nick else self.config["nickname"]
        self.send("NICK :{}".format(nick))

    def identify(self, params = None) :
        """Identifies the bot on the network"""
        if self.config["nickpass"] :
            utils.log().info("Identifying as {} on {}...".format(self.config["nickname"],
                                                              self.config["name"]))

            self.send("PRIVMSG {} :identify {} {}".format(self.config["nickserv"],
                                                          self.config["nickname"],
                                                          utils.password.decode(self.config["nickpass"])))

            self.nick()

    # General Message Types
    def message(self, target, message) :
        """Sends a message to a target on the network"""
        self.send("PRIVMSG {} :{}".format(target, message))

    def notice(self, target, message) :
        """Sends a notice to a target on the network"""
        self.send("NOTICE {} :{}".format(target, message))

    def reply(self, message, params) :
        """Sends a message to the invoker of a command"""
        self.message(params[1][2], message)

    # Network Events
    def _pong(self, host) :
        """PING"""
        self.send("PONG :{}".format(host[1:]))

    def _message(self, params) :
        """When PRIVMSG and NOTICE are received"""
        msg = params[3]

        if msg[0] == self.config["command"] :
            parts = msg.split(" ", 1)
            cmd = parts[0][1:]
            flags = parts[1] if (len(parts) > 1) else False

            self.bot.triggerCommand(self, cmd, (flags, params))

    def _connected(self, params) :
        """When the bot has successfully connected"""
        utils.log().info("Connection established ({})".format(self.config["name"]))
        self.identify()
        self.connected()

    def _nick(self, params) :
        """When a nickname is changed"""
        if params[0].nick == self.config["nickname"] :
            self.config["nickname"] = params[1]

    def _mode(self, params) :
        """When a mode is changed"""
        if params[2] == self.config["nickname"] :
            modes = params[3]
            action = "append" if modes[0] == "+" else "remove"

            for m in modes[1:] :
                if m == "r" and action == "append" :
                    utils.log().info("Identified on {}".format(self.config["name"]))
                    self.identified()
                    self.joinChannels()

                getattr(self.modes, action)(m)

    def _joined(self, params) :
        """When somebody joins a channel"""
        if params[0].nick == self.config["nickname"] :
            utils.log().info("{} joined {}".format(self.config["nickname"], params[1]))
            self.channels[params[1].lower()].joined()
        else :
            self.channels[params[1].lower()].users.append(params[2])

    def _kicked(self, params) :
        """When somebody is kicked from a channel"""
        kicked = params[3].split(" ", 1)
        if kicked[0] == self.config["nickname"] :
            utils.log().info("{} kicked from {} on {} ({})".format(self.config["nickname"],
                                                                params[2],
                                                                self.config["name"],
                                                                kicked[1][1:]))
            self.channels[params[2].lower()].join()
