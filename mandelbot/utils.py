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
    file = None

    def __init__(self, file = None) :
        self.file = file

        try :
            with open(self.file, "r") as _ :
                pass

        except :
            print("GRR")

    def open(self) :
        with open(file, "r") as fp :
            config = json.load(fp)
            return config
