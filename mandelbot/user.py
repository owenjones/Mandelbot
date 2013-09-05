# Mandelbot
"""
UserList - a list of users on the network that can be sorted through.
"""
class userList(object) :
    users = {}


"""
User model
"""
class user(object) :
    host = None
    channels = {}

    def __init__(self, hoststr) :
        self.host = host(hoststr)

"""
Host Model
"""
class host(object) :
    raw = None
    nick = None
    user = None
    host = None

    def __init__(self, addr) :
        """Splits a received host string into nickname, username and host"""
        addr = addr[1:]
        self.raw = addr
        nsplit = addr.find("!")
        hsplit = addr.find("@")
        self.nick = addr[:nsplit] if (nsplit > 0) else addr
        self.user = addr[(nsplit + 1):hsplit] if (nsplit > 0) else False
        self.host = addr[(hsplit + 1):] if (hsplit > 0) else addr
