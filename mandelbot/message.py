# Mandelbot
"""
Message Parsing
"""
def parse(raw) :
    return message(raw)

"""
Message Model
"""
class message(object) :
    raw = None
    action = None
    sender = None
    target = None
    message = None

    command = None
    flags = None

    def __init__(self, raw) :
        """Splits a received message into its relevant parts"""
        self.raw = raw.strip()
        parts = self.raw.split(" ", 3)

        if parts[0] == "PING" :
            self.action = parts[0]
            self.message = self.tidy(parts[1])
            return

        elif parts[1] in ("JOIN", "NICK", "PART") :
            self.action = parts[1]
            self.sender = host(parts[0])
            self.message = self.tidy(parts[2])
            return

        else :
            sender, self.action, target, message = parts
            self.sender = host(sender)
            self.target = target if (target.startswith("#") or self.action == "MODE") else self.sender.nick
            self.message = self.tidy(message)
            return

    def tidy(self, m) :
        """Strips the inital colon from the message, if it's present"""
        return m[1:] if m[0] is ":" else m

    def commander(self, command, flags) :
        """Adds the command data to the message object"""
        self.command = command
        self.flags = flags

"""
Host String Model
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
