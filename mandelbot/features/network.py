# Mandelbot
"""
Mandelbot Basic Network Commands
"""
import sys
from mandelbot.decorators import owner, user

def initalise(bot) :
    current = sys.modules[__name__]
    bot.registerCommand("quit", (current, "quit"))
    bot.registerCommand("shutdown", (current, "shutdown"))
    bot.registerCommand("join", (current, "join"))
    bot.registerCommand("part", (current, "part"))
    bot.registerCommand("!", (current, "exec"))

@owner
def quit(obj, flags) :
    obj.quit(flags[0])

@owner
def shutdown(obj, flags) :
    obj.shutdown(flags[0])

@user
def join(obj, flags) :
    parts = flags[0].split(" ", 1)
    chan = parts[0]
    key = parts[1] if len(parts) > 1 else False

    obj.join(chan, key)

@user
def part(obj, flags) :
    if flags[0] and flags[0][0] == "#" :
        parts = flags[0].split(" ", 1)
        chan = parts[0]
        message = parts[1] if len(parts) > 1 else False

    else :
        chan = flags[1][2]
        message = flags[0]

    obj.channels[chan].part(message)

@owner
def exec(obj, flags) :
    obj.message(flags[1][2], eval(flags[0]))
