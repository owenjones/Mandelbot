"""
Message Parsing

Provides methods to parse incoming messages from an IRC network, and to
register callbacks for commands.
"""
import re
from . import utils

class parser(object) :
    network = None
    builtin = {}
    callbacks = {}

    def __init__(self, network) :
        self.network = network

        self.builtin = {"PING"    : (self.network, "pong"),
                        "NOTICE"  : (self, "message"),
                        "PRIVMSG" : (self, "message"),
                        "KICK"    : (self.network, "kicked"),
                        "NICK"    : (self.network, "nickchange"),
                        "ERROR"   : (self, "error")}

    def host(self, line) :
        return False

    def call(self, call, param) :
        try :
            call = self.builtin[call]
            print("Calling {}".format(call))
            getattr(call[0], call[1])(param)

        except KeyError :
            pass

    def parse(self, raw) :
        try :
            print(raw)
            test = raw.split(" ", 1)
            if test[0] in ("PING", "ERROR") :
                self.call(test[0], test[1])
                return

            addr, cmd, tgt, msg = raw.split(" ", 3)


        except Exception as e :
            utils.console(str(e))