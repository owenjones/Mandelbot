# MANDELBOT
"""
Provides basic utilties for running Mandelbot
"""
import time, json

def console(message) :
    print("[{}] {}".format(logtime(), message))

def logtime(t = None) :
    t = t if t else time.time()
    return time.strftime("%H:%M:%S", time.localtime(t))

class config(object) :
    _file = None

    def __init__(self, file = None) :
        self._file = file

    def load(self, file = None) :
        with open(file, "r") as conf :
            config.parse(conf)

    def parse(self) :
        pass

    def save(self) :
        pass
