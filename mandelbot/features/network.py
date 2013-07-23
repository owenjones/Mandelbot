# Mandelbot
"""
Mandelbot Basic Network Commands
"""
import sys
from mandelbot.decorators import owner, user
from mandelbot import utils, features

def initalize(bot) :
    current = sys.modules[__name__]
    bot.registerCommand("quit", (current, "quit"))
    bot.registerCommand("shutdown", (current, "shutdown"))
    bot.registerCommand("join", (current, "join"))
    bot.registerCommand("part", (current, "part"))
    bot.registerCommand("load", (current, "load"))
    bot.registerCommand("!", (current, "run"))
    bot.registerCommand("tell", (current, "message"))

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
def load(obj, flags) :
    if flags[0] :
        feature = flags[0].split()

        for f in feature :
            try :
                features.load(obj.bot, f)

            except (ImportError, KeyError) :
                obj.reply("[\x02Feature Error\x02] \"{}\" doesn't exist.".format(f), flags)

            except Exception as e :
               obj.reply("[\x02Feature Error\x02 {}] {}".format(f, e), flags)

@owner
def run(obj, flags) :
    reply = exec(flags[0])

    if reply :
        obj.reply(reply, flags)

@user
def message(obj, flags) :
    p = flags[0].split(" ", 1)
    target = flags[1][2] if p[0] == "chan" else p[0]
    obj.message(target, p[1])
