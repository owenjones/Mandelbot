# MANDELBOT
"""
Provides basic utilties for running Mandelbot
"""
import time, base64, json

def console(message) :
    """Desplays a formatted message on the terminal"""
    formatted = "[{}] {}".format(logtime(), message)
    print(formatted)

def logtime(t = None) :
    """Returns the time in a log-friendly format"""
    t = t if t else time.time()
    return time.strftime("%H:%M:%S", time.localtime(t))

def host(addr) :
    """Splits a received host string into nickname, username and host"""
    addr = addr[1:]
    nsplit = addr.find("!")
    hsplit = addr.find("@")
    nick = addr[:nsplit] if (nsplit > 0) else addr
    user = addr[(nsplit + 1):hsplit] if (nsplit > 0) else False
    host = addr[(hsplit + 1):] if (hsplit > 0) else addr

    return {"nick": nick, "user": user, "host": host}

"""
Password Methods
Handle encoding and decoding network and user passwords for slightly "safer" storage
(Stops people from being able to straight-up read your password from the config)
"""
class password(object) :

    def encode(p) :
        """Returns an encoded password as a string"""
        return base64.b64encode(p.encode("UTF-8")).decode("UTF-8")

    def decode(p) :
        """Returns a decoded password as a string"""
        return base64.b64decode(p.encode("UTF-8")).decode("UTF-8")

"""
Configuration Methods
"""
class config(object) :
    file = None
    loaded = {}

    def __init__(self, file = None) :
        """Initiates the configuration session using the specified file"""
        self.file = file

    def __getattr__(self, name) :
        try :
            return self.loaded[name]

        except KeyError :
            return False

    def load(self) :
        """Loads the configuration from the configuration file"""
        try :
            with open(self.file, "r") as fp :
                self.loaded = json.load(fp)
                fp.close()

        except (FileNotFoundError, ValueError) :
            console("Invalid configuration file \"{}\", please run Mandelbot using the --build flag first".format(self.file))
            exit(console("Aborting Mandelbot launch..."))

    def build(self, networks = []) :
        """Takes a list of network objects, strips the configurations
        from each and packages them in a dictionary to be stored"""
        console("Building new configuration...")

        try :
            assert(isinstance(networks, list))
            assert(len(networks) > 0)

            conf = {}
            nets = []

            for n in networks :
                nets.append(n.config)

            if nets :
                conf["networks"] = nets

            self._save(conf)

        except AssertionError :
            console("Building configuration failed - invalid data structure")

        except Exception as e :
            console("Building configuration failed - {}".format(e))

    def _save(self, new) :
        """Replaces the current configuration file with an updated one"""
        try :
            with open(self.file, "w") as fp :
                json.dump(new, fp)
                fp.close()

            console("Configuration saved as \"{}\"".format(self.file))

        except Exception as e :
            console("Saving configuration failed - {}".format(e))
