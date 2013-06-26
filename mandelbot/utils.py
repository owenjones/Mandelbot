# MANDELBOT
"""
Provides basic utilties for running Mandelbot
"""
import time, json, base64

def console(message) :
    print("[{}] {}".format(logtime(), message))

def logtime(t = None) :
    t = t if t else time.time()
    return time.strftime("%H:%M:%S", time.localtime(t))

"""
Password Methods
Handle encoding/decoding network and user passwords for slightly safer storage

encode (str) - Returns an encoded string
decode (str) - Returns a decoded password
"""
class password(object) :

    def encode(p) :
        return base64.b64encode(p.encode("UTF-8")).decode("UTF-8")

    def decode(p) :
        return base64.b64decode(p.encode("UTF-8")).decode("UTF-8")

"""
Configuration Methods
These deal with loading and saving configuration files

save (dict) - Replaces the current configuration file with an updated one
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

    def save(self, new) :
        try :
            assert(isinstance(new, dict))
            assert(isinstance(new["networks"], list))

            with open(self.file, "w") as fp :
                json.dump(new, fp)

        except AssertionError :
            utils.console("Updating configuration failed - invalid data structure")

        except Exception as e :
            utils.console("Updating configuration failed - {}".format(e.strerror))


class message(object) :

    def parse(data) :
        return data
