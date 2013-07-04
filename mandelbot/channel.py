#Mandelbot
"""
Channel model
"""
class channel(object) :
    name = None
    network = None
    key = None
    modes = []
    users = []
    joined = False

    def __init__(self, network, name, key) :
        self.name = name
        self.network = network
        self.key = key

    def join(self) :
        c = "JOIN {} {}".format(self.name,self.key) if self.key else "JOIN {}".format(self.name)
        self.network.send(c)

    def joined(self) :
        self.joined = True

    def part(self, message = None) :
        c = "PART {} {}".format(self.name, message) if message else "PART {}".format(self.name)
        self.network.send(c)
        self.joined = False
