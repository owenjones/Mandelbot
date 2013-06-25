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

def config(file = None) :
    with open(file, "r") as fp :
        config = json.load(fp)
        return config
