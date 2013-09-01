# Mandelbot
"""
IRC network model.
Handles establishing a connection to, and interacting with, the IRC network.

TODO:
* Implement anti-flooding (buffer & time limit)
* Allow quiet mode to be applied on a per-channel basis
* Work out better timeout metrics
"""
import threading, time
from . import utils, connection, channel, message
from .exceptions import *

"""
Network States

Lots of flags to keep track of what the bot is doing,
and a few methods to alter groups of them
"""
class state(object) :
    isConnected = False
    isReconnecting = False
    isTimingOut = False
    isTimedOut = False
    isQuitting = False

    isIdentified = False
    isQuiet = False
    currentNickname = False

    def reset(self) :
        """Reset all the flags to their default values"""
        self.isConnected = False
        self.isReconnecting = False
        self.isTimingOut = False
        self.isTimedOut = False
        self.isQuitting = False

        self.isIdentified = False
        self.isQuiet = False
        self.currentNickname = False

    def connected(self) :
        """We've connected to the network"""
        self.isConnected = True
        self.isTimedOut = False
        self.isReconnecting = False

class network(state) :
    bot = None
    connection = None
    delimiter = "\r\n"
    buff = []
    messages = []
    modes = []
    channels = {}
    config = {}

    events = {"PING"    : "_ping",
              "JOIN"    : "_joined",
              "MODE"    : "_modeChange",
              "NICK"    : "_nickChange",
              "KICK"    : "_kicked",
              "NOTICE"  : "_message",
              "PRIVMSG" : "_message",

              "001"     : "_connected",
              "433"     : "_nickInUse"}

    timer = None

    def __init__(self, config, bot) :
        self.bot = bot
        self.config = config

    def event(self, m) :
        """Triggers the handler for the network event"""
        try :
            attr = self.events[m.action]

        except KeyError :
            return

        try :
            getattr(self, attr)(m)

        except Exception as e :
            utils.log().error("[{}][Builtin Error {}] {}".format(self.config["name"], m.action, e))

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
            utils.log().error("[{}] Connection information is invalid.".format(self.config["name"]))

        except CouldNotConnect :
            utils.log().error("[{}] Could not connect to network.".format(self.config["name"]))
            if not self.isReconnecting :
                self._reconnect()

    def parse(self, raw) :
        """Parses a received message from the network"""
        self._resetTimeout()
        m = message.parse(raw)
        utils.log().debug("[{}] Received: {}".format(self.config["name"], m.raw))
        self.event(m)

    def send(self, message) :
        """Sends a message to the network"""
        utils.log().debug("[{}] Sent: {}".format(self.config["name"], message))
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
        utils.log().info("[{}] Quitting.".format(self.config["name"]))
        self.send(q)
        self.isQuitting = True
        self.timer.cancel()
        self.connection.close(True)

    def shutdown(self, message) :
        """Gracefully closes the connection to all networks, and halts the bot"""
        bot.shutdown(message)

    # Nickname Managment
    def nick(self, nick = None) :
        """Changes the bot's nickname on the network"""
        nick = nick if nick else self.config["nickname"]
        self.currentNickname = nick
        self.send("NICK :{}".format(nick))

    def identify(self, params = None) :
        """Identifies the bot on the network"""
        if self.config["nickpass"] :
            utils.log().info("[{}] Identifying as {}...".format(self.config["name"],
                                                              self.config["nickname"]))

            self.send("PRIVMSG {} :identify {} {}".format(self.config["nickserv"],
                                                          self.config["nickname"],
                                                          utils.password.decode(self.config["nickpass"])))

    def ghost(self, params = None) :
        """Mandelbot's nickname is already in use - get it back!"""
        if self.config["nickpass"] :
            self.send("PRIVMSG {} :ghost {} {}".format(self.config["nickserv"],
                                                       self.config["nickname"],
                                                       utils.password.decode(self.config["nickpass"])))

        self.nick()

    # General Message Types
    def ping(self) :
        self.send("PING :{}".format(self.config["host"]))

    def message(self, target, message) :
        """Sends a message to a target on the network"""
        if (self.isQuiet and not target.startswith("#")) or not self.isQuiet :
            self.send("PRIVMSG {} :{}".format(target, message))

    def notice(self, target, message) :
        """Sends a notice to a target on the network"""
        self.send("NOTICE {} :{}".format(target, message))

    def reply(self, message, m) :
        """Sends a message to the invoker of a command"""
        self.message(m.target, message)

    # Network Events
    def _ping(self, m) :
        """PING"""
        self.send("PONG :{}".format(m.message))

    def _message(self, m) :
        """When PRIVMSG and NOTICE are received"""
        if m.message.startswith(self.config["command"]) :
            parts = m.message.split(" ", 1)
            cmd = parts[0][len(self.config["command"]):]
            flags = parts[1] if (len(parts) > 1) else False
            m.commander(cmd, flags)

            self.bot.triggerCommand(self, m)

    def _connected(self, m) :
        """When the bot has successfully connected"""
        utils.log().info("[{}] Connection established.".format(self.config["name"]))
        self.connected()
        self.identify()

    def _identified(self, m) :
        """We're now identified"""
        utils.log().info("[{}] Identified.".format(self.config["name"]))
        self.isIdentified = True

        # Required if nickname needed to be changed during a reconnect
        if m.target != self.config["nickname"] :
            self.ghost()

        self.joinChannels()

    def _nickInUse(self, m) :
        self.nick(self.config["nickname"] + "_")

        if self.isIdentified :
            self.ghost()

    def _nickChange(self, m) :
        if m.sender.nick == self.currentNickname :
            self.currentNickname == m.message

    def _modeChange(self, m) :
        """When a mode is changed"""
        if m.target.startswith("#") :
            #self.channels[m.target].modeChange(m)
            pass

        elif m.target == self.currentNickname :
            modes = m.message
            action = "append" if modes[0] == "+" else "remove"

            for mod in modes[1:] :
                if mod == "r" and action == "append" :
                    self._identified(m)

                getattr(self.modes, action)(mod)

    def _joined(self, m) :
        """When somebody joins a channel"""
        if m.sender.nick == self.currentNickname :
            utils.log().info("[{}] Joined {}.".format(self.config["name"], m.message))
            self.channels[m.message.lower()].joined()
        else :
            #self.channels[params[1].lower()].users[params[2].nick] =
            pass

    def _kicked(self, m) :
        """When somebody is kicked from a channel"""
        kicked = m.message.split(" ", 1)
        if kicked[0] == self.currentNickname :
            utils.log().info("[{}] Kicked from {}. ({})".format(self.config["name"],
                                                                m.target,
                                                                kicked[1][1:]))
            self.channels[m.target.lower()].join()

    # Timeout Handling
    def _timer(self, time, call, *args) :
        """Creates a new timer"""
        if self.timer :
            self.timer.cancel()

        self.timer = threading.Timer(time, call, args)
        self.timer.start()

    def _resetTimeout(self) :
        """Resets the timer that checks for disconnects"""
        if not self.isQuitting :
            self.isTimingOut = False
            self.isTimedOut = False
            self._timer(120, self._timeoutCheck)

    def _timeoutCheck(self) :
        """Occurs when the connection has been quiet for too long"""
        if not self.isTimingOut :
            self.isTimingOut = True
            self.ping()
            self._timer(30, self._timeout)

    def _timeout(self) :
        """Connection is unresponsive - attempt to reconnect"""
        self.connection.thread.stop()
        self.connection = None
        self.reset()
        self.isTimedOut = True
        utils.log().warning("[{}] Connection timed out.".format(self.config["name"]))
        self._reconnect()

    def _reconnect(self, n = 0) :
        self.isReconnecting = True

        if n < 5 :
            utils.log().warning("[{}] Attempting to reconnect ({} of 5)".format(self.config["name"], n+1))
            self._timer(30, self._reconnect, (n+1))
            self.connect()

        else :
            utils.log().warning("[{}] Could not reconnect. Will try again shortly.".format(self.config["name"]))
            self._timer(120, self._reconnect)
