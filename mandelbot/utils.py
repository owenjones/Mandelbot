# Mandelbot
"""
Provides basic utilties for running Mandelbot
"""
import time, base64, json, argparse, logging

def flags() :
    """Parses the arguments Mandelbot is run with"""
    p = argparse.ArgumentParser(description="Runs an instance of the Mandelbot IRC bot")
    p.add_argument("-b", "--build", action="store_true", help="Creates a Mandelbot configuration file")
    p.add_argument("-v", "--verbose", action="count", default = 0, help="Display console messages during the running of Mandelbot")
    p.add_argument("-f", "--features", action="store_true",
                        help="Automatically load all the features in the features directory on Mandelbot startup")
    p.add_argument("-i", "--interactive", action="store_true", help = "Run Mandelbot interactively")
    p.add_argument("-c", "--config", dest="config",
                   help="Specify a different Mandelbot configuration to use")

    arg = p.parse_args()
    return arg

def loginit(verbosity) :
    _LEVELS = {
        0 : logging.ERROR,
        1 : logging.INFO,
        2 : logging.DEBUG,
    }

    l = log()
    h = logging.StreamHandler()
    h.setLevel(_LEVELS[verbosity])
    f = logging.Formatter("[%(asctime)s] %(message)s")
    h.setFormatter(f)
    l.addHandler(h)
    l.setLevel(_LEVELS[verbosity])

def log() :
    """Returns the logger object for the bot"""
    l = logging.getLogger()
    return l

def console(message) :
    """Displays a formatted message on the terminal"""
    formatted = "[{}] {}".format(logtime(), message)
    print(formatted)

def logtime(t = None) :
    """Returns the time in a log-friendly format"""
    t = t if t else time.time()
    return time.strftime("%H:%M:%S", time.localtime(t))

class host(object) :

    def __init__(self, addr) :
        """Splits a received host string into nickname, username and host"""
        addr = addr[1:]
        nsplit = addr.find("!")
        hsplit = addr.find("@")
        self.nick = addr[:nsplit] if (nsplit > 0) else addr
        self.user = addr[(nsplit + 1):hsplit] if (nsplit > 0) else False
        self.host = addr[(hsplit + 1):] if (hsplit > 0) else addr


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

        except (FileNotFoundError, ValueError) as e :
            log().critical("Invalid configuration file \"{}\", please run Mandelbot using the --build flag first".format(self.file))
            log().info("Aborting Mandelbot launch.")
            exit()

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
            log().error("Building configuration failed - invalid data structure")

        except Exception as e :
            log().error("Building configuration failed - {}".format(e))

    def _save(self, new) :
        """Replaces the current configuration file with an updated one"""
        try :
            with open(self.file, "w") as fp :
                json.dump(new, fp)
                fp.close()

            log().info("Configuration saved as \"{}\"".format(self.file))

        except Exception as e :
            log().error("Saving configuration failed - {}".format(e))
