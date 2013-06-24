# MANDELBOT
__title__ = "Mandelbot"
__version__ = "0.1a"
__author__ = "Owen Jones"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2013 Owen Jones"

from . import utils

def run(config = None) :
    utils.console("{} {} is launching..".format(__title__, __version__))
    Mandelbot(config)

class Mandelbot(object) :
    config = None
    modules = []
    networks = []
    hooks = []

    def __init__(self, conf = None) :
        conf = conf if conf else "config.json"
        self.config = utils.config(conf)
        self.config.load()
        self.loadModules()
        self.loadNetworks()

    def loadNetworks(self) :
        for net in self.config.networks :
            self.networks.append(net)
            if net.autoconnect :
                self.network(net.name).connect

    def loadModules(self) :
        pass

    def network(self, match) :
        for net in self.networks :
            if net.config["name"]  == match :
                return net
