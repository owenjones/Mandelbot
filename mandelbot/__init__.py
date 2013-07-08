# MANDELBOT
__title__ = "Mandelbot"
__version__ = "0.1a"
__author__ = "Owen Jones"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2013 Owen Jones"

from . import utils, network
from .exceptions import *

def run(config = None) :
    utils.console("{} {} is launching..".format(__title__, __version__))
    Mandelbot(config)

class Mandelbot(object) :
    config = None
    modules = []
    networks = []

    def __init__(self, conf = None) :
        conf = conf if conf else "config.json"
        self.config = utils.config(conf)
        self.config.load()

        self.loadNetworks()
        self.loadModules()

    def loadNetworks(self) :
        for n in self.config.networks :
            net = network.network(n, self)
            self.networks.append(net)
            if n["autoconnect"] :
                net.connect()

    def loadModules(self) :
        pass

    def shutdown(self, message = None) :
        utils.console("Shutting down...")
        message = message if message else "Mandelbot IRC Bot ({})".format(__version__)
        for n in self.networks :
            if n.state.isConnected :
                n.quit(message)

        self.config.build(self.networks, self.modules)
