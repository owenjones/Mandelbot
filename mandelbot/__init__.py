# MANDELBOT
__title__ = "Mandelbot"
__version__ = "0.1a"
__author__ = "Owen Jones"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2013 Owen Jones"

from mandelbot import utils, network, features

def run(config = None) :
    utils.console("{} {} is launching..".format(__title__, __version__))
    Mandelbot(config)

class Mandelbot(object) :
    config = None
    networks = []
    commands = {}

    def __init__(self, conf = None) :
        conf = conf if conf else "config.json"
        self.config = utils.config(conf)
        self.config.load()
        self.loadNetworks()
        features.loadall(self)

    def loadNetworks(self) :
        for n in self.config.networks :
            net = network.network(n, self)
            self.networks.append(net)
            if n["autoconnect"] :
                net.connect()

    def loadFeature(self, feature) :
        features.reload(self, feature)

    def registerCommand(self, command, call) :
        self.commands[command] = call

    def triggerCommand(self, net, command, params) :
        try :
            call = self.commands[command]

        except KeyError :
            net.reply("Command \"{}\" not registered".format(command), params)
            return

        try :
            getattr(call[0], call[1])(net, params)

        except Exception as e :
            net.reply("Error with command: [{}]".format(e), params)

    def shutdown(self, message = None) :
        utils.console("Shutting down...")
        message = message if message else "Mandelbot IRC Bot ({})".format(__version__)
        for n in self.networks :
            if n.isConnected :
                n.quit(message)

        self.config.build(self.networks)
