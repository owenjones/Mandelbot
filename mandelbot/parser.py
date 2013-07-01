"""
Message Parsing

Provides methods to parse incoming messages from an IRC network, and to
register callbacks for commands.
"""
from . import utils

class parser(object) :
    network = None
    builtin = {}
    callbacks = {}

    def __init__(self, network) :
        self.network = network

        self.builtin = {"PING"    : (self.network, "pong"),
                        "NOTICE"  : (self, "_notice"),
                        "PRIVMSG" : (self, "_privmsg")}

    def call(self, call, param) :
        try :
            call = self.builtin[call]
            print("Calling {}".format(call))

        except KeyError :
            try :
                call = self.callbacks[call]

            except KeyError :
                utils.console("Callback {} not found".format(call))

        try :
            getattr(call[0], call[1])(param)

        except Exception as e :
            utils.console(str(e))

    def parse(self, raw) :
        try :
            a, b = raw.split(" :")
            parsed = {}

            if a.strip() == "PING" :
                self.call("PING", b)

        except Exception as e :
            utils.console(str(e))
