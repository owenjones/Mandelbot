# Mandelbot
from .user import host

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
            self.sender = user.host(parts[0])
            self.message = self.tidy(parts[2])
            return

        else :
            sender, self.action, target, message = parts
            self.sender = user.host(sender)
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
