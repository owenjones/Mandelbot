# MANDELBOT
__title__ = "Mandelbot"
__version__ = "0.1a"
__author__ = "Owen Jones"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2013 Owen Jones"

from . import utils, network

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
        config = utils.config(conf)

        for n in config["networks"] :
            net = network.network(n)
            self.networks.append(net)
            if n["autoconnect"] :
                net.connect()
