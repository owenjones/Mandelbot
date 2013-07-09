"""
Message Parsing

Provides methods to parse incoming messages from an IRC network, and to
register callbacks for commands.
"""
from . import utils

class parser(object) :
    network = None
    builtin = {}
    callback = {}

    def __init__(self, network) :
        self.network = network

        self.builtin = {"PING"    : (self.network, "pong"),

                        # Trigger Network Events
                        "001"     : (self.network, "connected"),
                        "JOIN"    : (self.network, "joined"),
                        "NICK"    : (self.network, "nickchanged"),
                        "MODE"    : (self.network, "modechanged"),
                        "KICK"    : (self.network, "kicked"),

                        # Handle received messages
                        "NOTICE"  : (self, "message"),
                        "PRIVMSG" : (self, "message")}

        self.callback = {"quit"      : (self.network, "cmd_quit"),
                         "shutdown"  : (self.network, "cmd_shutdown"),
                         "join"      : (self.network, "cmd_join"),
                         "part"      : (self.network, "cmd_part"),
                         "callbacks" : (self.network, "cmd_callbacks"),
                         "builtins"  : (self.network, "cmd_builtins"),
                         "!"         : (self.network, "cmd_exec")}

    def host(self, addr) :
        addr = addr[1:]
        nsplit = addr.find("!")
        hsplit = addr.find("@")
        nick = addr[:nsplit] if (nsplit > 0) else addr
        user = addr[(nsplit + 1):hsplit] if (nsplit > 0) else False
        host = addr[(hsplit + 1):] if (hsplit > 0) else addr

        return {"nick": nick, "user": user, "host": host}

    def callBuiltin(self, call, params) :
        try :
            call = self.builtin[call]

        except KeyError :
            # Means we don't have to define a builtin for every single IRC command
            return

        try :
            getattr(call[0], call[1])(params)

        except Exception as e :
            utils.console("Error with builtin: [{}]".format(e))

    def callCallback(self, cmd, params) :
        try :
            call = self.callback[cmd]

        except KeyError :
            self.network.message(params[1][2], "Command \"{}\" not registered".format(cmd))
            break

        try :
            getattr(call[0], call[1])(params)

        except AttributeError :
            self.network.message(params[1][2], "Command \"{}\" not registered".format(cmd))

        except Exception as e :
            utils.console("Error with command: [{}]".format(e))
            self.network.message(params[1][2], "Error with command: [{}]".format(e))

    def parse(self, raw) :
        parts = raw.strip().split(" ", 3)
        if parts[0] == "PING" :
            self.callBuiltin("PING", parts[1])

        elif parts[1] in ("JOIN", "NICK", "PART") :
            addr = self.host(parts[0])
            msg = parts[2][1:] if parts[2][0] == ":" else parts[2]
            self.callBuiltin(parts[1], (addr, msg))

        else :
            addr, cmd, tgt, msg = parts
            addr = self.host(addr)

            if tgt[0] != "#" :
                tgt = self.network.config["nickname"] if cmd == "MODE" else addr["nick"]

            msg = msg[1:] if msg[0] is ":" else msg

            self.callBuiltin(cmd, (addr, cmd, tgt, msg))

    def message(self, params) :
        msg = params[3]

        if msg[0] == self.network.config["command"] :
            parts = msg.split(" ", 1)
            cmd = parts[0][1:]
            flags = parts[1] if (len(parts) > 1) else False

            self.callCallback(cmd, (flags, params))
