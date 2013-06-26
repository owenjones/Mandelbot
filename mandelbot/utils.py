# MANDELBOT
"""
Provides basic utilties for running Mandelbot
"""
import time, base64, json

def console(message) :
    print("[{}] {}".format(logtime(), message))

def logtime(t = None) :
    t = t if t else time.time()
    return time.strftime("%H:%M:%S", time.localtime(t))

"""
Password Methods
Handle encoding/decoding network and user passwords for slightly safer storage

encode (str) - Returns an encoded password as a string
decode (str) - Returns a decoded password as a string
"""
class password(object) :

    def encode(p) :
        return base64.b64encode(p.encode("UTF-8")).decode("UTF-8")

    def decode(p) :
        return base64.b64decode(p.encode("UTF-8")).decode("UTF-8")

"""
Configuration Methods
These deal with loading and saving configuration files

build - Takes a list of network and module objects, strips the configurations
      - from each and packages them in a dictionary to be stored

save  - Replaces the current configuration file with an updated one
"""
class config(object) :
    file = None
    loaded = {}

    def __init__(self, file = None) :
        self.file = file

        with open(file, "r") as fp :
            self.loaded = json.load(fp)

    def __getattr__(self, name) :
        return self.loaded[name]

    def build(self, networks = [], modules = []) :
        conf = {}
        nets = []
        mods = []

        for n in networks :
            nets.append(n.config)

        for m in modules :
            mods.append(m.config)

        if nets :
            conf["networks"] = nets

        if mods :
            conf["modules"] = mods

        self.save(conf)


    def save(self, new) :
        try :
            assert(isinstance(new, dict))
            assert(isinstance(new["networks"], list))

            assert(len(new["networks"]) > 0)

            if new["modules"] :
                assert(isinstance(new["modules"], list))

            with open(self.file, "w") as fp :
                json.dump(new, fp)

        except AssertionError :
            utils.console("Updating configuration failed - invalid data structure")

        except Exception as e :
            utils.console("Updating configuration failed - {}".format(str(e)))


class message(object) :

    def parse(data) :
        return data
