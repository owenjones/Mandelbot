# MANDELBOT
"""
IRC network model.
Handles establishing a connection to, and interacting with, the IRC network.

TODO:
* Implement anti-flooding (buffer & time limit)

Properties:
c (object)                 - the established connection to the IRC server
parser (object)            - the message parser object for this network
delimiter (str)            - the character(s) that break up messages being sent to the network
buff (list)                - a list of messages waiting to be sent to the IRC network (prevents flooding)
messages (list)            - a list of messages received from the IRC network
connected (bool)           - whether the network is connected or not

config: name (str)         - the name of the network
        host (str)         - the address of the IRC network server
        port (int)         - the port the IRC server listens on
        ssl (bool)         - whether to connect using SSL or not
        password (str)     - the password for the IRC server (if required)
        autoconnect (bool) - whether to automatically connect to the IRC server when Mandelbot is launched
        nickserv (str)     - the identification service on this network
        username (str)     - used to identify Mandelbot with the IRC server
        nickpass (str)     - used to identify Mandelbot with the IRC server
        realname (str)     - used to identify Mandelbot with the IRC server
        nickname (str)     - used to identify Mandelbot with the IRC server
        command (str)      - the command identifier Mandelbot listens for on this network
        owner (str)        - the IRC user who can administrate Mandelbot on this network
        users (list)       - a list of IRC users who can access Mandelbot's protected functions on this network
        chans (dict)       - a dictionary of the channels Mandelbot is connected to, along with the modes Mandelbot has been granted on them

Methods:
connect                    - attempts to create a connection to the IRC server
identify                   - identifies Mandelbot with the IRC network
send                       - sends a message to the specified channel or user
notice                     - sends a notice to the specified channel or user
join                       - joins a channel on the network
part                       - leaves a channel on the network
quit                       - leaves the IRC network and closes the connection to the server

Internal Methods:
_receive                   - receives a message from the network and handles it
"""
from . import connection, utils, parser
from .exceptions import *
import time

class network(object) :
    c = None
    parser = None
    delimiter = "\r\n"
    buff = []
    messages = []
    connected = False
    config = {} # This will be populated when the network is loaded from the configuration

    def __init__(self, config) :
        self.config = config
        self.parser = utils.parser(self)

    def connect(self) :
        try :
            self.c = connection.connection(self.config["host"], self.config["port"], self.config["ssl"], False)
            self.c.connect()
            utils.console("Connection established ({})".format(self.config["name"]))
            self.c.handler = (self, "_receive")

            if self.config["password"] :
                self.send("PASS {}".format(utils.password.decode(self.config["password"])))

            utils.console("Identifying as {} on {}...".format(self.config["nickname"], self.config["name"]))
            self.send("USER {} * * :{}".format(self.config["username"], self.config["realname"]))
            self.send("NICK {}".format(self.config["nickname"]))

            self.testloop()

        except InvalidConnectionInformation :
            raise InvalidServer

        except CouldNotConnect :
            raise NoServerConnection

    """
    Just for testing...
    """
    def testloop(self) :
        time.sleep(5)
        self.send("JOIN ##mandelbottesting")

        try :
            while True :
                    inp = input("SEND> ")
                    if inp == "QUIT" :
                        self.quit("Via Command ({})".format(utils.logtime()))
                        break

                    elif inp == "FLOOD" :
                        for _ in range(8) :
                            self.send("PRIVMSG ##mandelbottesting :Flooding test")

                    elif "+exec" in inp :
                        try :
                            exec(inp.strip("+exec "))
                        except Exception as e :
                            utils.console("Bad command: {}".format(str(e)))
                    else :
                        self.send(inp)
        except KeyboardInterrupt :
            self.quit("Via KeyboardInterrupt")

    def nickname(self, nick) :
        self.config["nickname"] = nick
        self.send("NICK :{}".format(nick))

    def identify(self) :
        if self.config["nickpass"] :
            self.send("PRIVMSG {} :identify {} {}".format(self.config["nickserv"], self.config["username"], utils.password.decode(self.config["nickpass"])))

    def pong(self, returned) :
        self.send("PONG :{}".format(returned["data"]))

    def quit(self, message = None) :
        q = "QUIT :{}".format(message) if message else "QUIT"
        self.send(q)
        self.close()

    def close(self) :
        self.c.close(True)

    def send(self, message) :
        message = message + self.delimiter
        print("SENDING: " + message)
        self.c.send(message)

    """
    Placeholder, eventually received messages will just be passed to the parser
    """
    def _receive(self, data) :
        print("RECEIVED: {}".format(data))
        message = self.parser.parse(data)

        if message["type"] == "PING" :
            self.send("PONG :{}".format(message["data"]))
