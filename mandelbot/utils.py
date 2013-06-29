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

    def __getattr__(self, name) :
        return self.loaded[name]

    def load(self) :
        try :
            with open(self.file, "r") as fp :
                self.loaded = json.load(fp)
                fp.close()

        except (FileNotFoundError, ValueError) :
            console("Invalid configuration file \"{}\", please run Mandelbot using the --build flag first".format(self.file))
            exit(console("Aborting Mandelbot launch..."))

    def build(self, networks = [], modules = []) :
        console("Building new configuration...")

        try :
            assert(isinstance(networks, list))
            assert(isinstance(modules, list))
            assert(len(networks) > 0)

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

            self._save(conf)

        except AssertionError :
            console("Building configuration failed - invalid data structure")

        except Exception as e :
            console("Building configuration failed - {}".format(e))

    def _save(self, new) :
        try :
            with open(self.file, "w") as fp :
                json.dump(new, fp)
                fp.close()

            console("Configuration saved as \"{}\"".format(self.file))

        except Exception as e :
            console("Saving configuration failed - {}".format(e))

"""
Message Parsing
"""
class parser(object) :
    network = None
    command = None
    callbacks = {}

    def __init__(self, network, command) :
        self.network = network
        self.command = command

    def parse(self, raw) :
        parsed = {}

        data = raw.split(" :")
        if "PING" == data[0] :
            parsed["type"] = "PING"
            parsed["data"] = data[1]
        else :
            parsed["type"] = "MSG"
            parsed["data"] = raw

        return parsed
