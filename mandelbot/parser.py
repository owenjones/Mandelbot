"""
Message Parsing
"""
class parser(object) :
    network = None
    command = None
    builtin = {"PING"    : (self.network, "pong"),
               "NOTICE"  : (self, "_notice"),
               "PRIVMSG" : (self, "_privmsg")}
    callbacks = {}

    def __init__(self, network) :
        self.network = network
        self.command = self.network.config["command"]

    def parse(self, raw) :
        command, data = raw.split(" :")
        parsed = {}
