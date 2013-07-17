"""
Message Parsing

Provides methods to parse incoming messages from an IRC network, and to
register callbacks for commands.
"""
from mandelbot import utils

class parser(object) :
    network = None
    builtin = {}

    def __init__(self, network) :
        self.network = network

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

    def parse(self, raw) :
        parts = raw.strip().split(" ", 3)
        #print(parts)
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

        if msg.startswith(self.network.config["command"]) :
            parts = msg.split(" ", 1)
            cmd = parts[0][len(self.network.config["command"]):]
            flags = parts[1] if (len(parts) > 1) else False

            self.network.bot.triggerCommand(self.network, cmd, (flags, params))
