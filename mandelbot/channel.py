#Mandelbot
"""
Channel model
"""
class channel(object) :
    network = None

    name = None
    key = None

    channelModes = []

    hasJoined = False
    isQuiet = False

    def __init__(self, network, name, key) :
        self.network = network
        self.name = name
        self.key = key

    def join(self) :
        c = "JOIN {} {}".format(self.name,self.key) if self.key else "JOIN {}".format(self.name)
        self.network.send(c)

    def joined(self) :
        self.hasJoined = True
        self.network.send("WHO {}".format(self.name))

    def part(self, message = None) :
        c = "PART {} {}".format(self.name, message) if message else "PART {}".format(self.name)
        self.network.send(c)
        self.hasJoined = False
