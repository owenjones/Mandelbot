# Mandelbot
"""
Mandelbot Basic Network Commands
"""
import sys
from ..decorators import owner, user
from .. import utils, features

def initalize(bot) :
    current = sys.modules[__name__]
    bot.registerCommand("quit", (current, "quit"))
    bot.registerCommand("shutdown", (current, "shutdown"))
    bot.registerCommand("join", (current, "join"))
    bot.registerCommand("part", (current, "part"))
    bot.registerCommand("cycle", (current, "cycle"))
    bot.registerCommand("load", (current, "load"))
    bot.registerCommand("!", (current, "run"))
    bot.registerCommand("quiet", (current, "quiet"))
    bot.registerCommand("tell", (current, "message"))

@owner
def quit(obj, m) :
    obj.quit(m.flags)

@owner
def shutdown(obj, m) :
    obj.shutdown(m.flags)

@user
def join(obj, m) :
    parts = m.flags.split(" ", 1)
    chan = parts[0]
    key = parts[1] if len(parts) > 1 else False

    obj.join(chan, key)

@user
def part(obj, m) :
    if m.flags and m.flags.startswith("#") :
        parts = m.flags.split(" ", 1)
        chan = parts[0]
        message = parts[1] if len(parts) > 1 else False

    else :
        chan = m.target
        message = m.flags

    obj.channels[chan].part(message)

@user
def cycle(obj, m) :
    chan = m.target
    key = obj.channels[chan].key
    obj.channels[chan].part("Boing")
    obj.join(chan, key)

@owner
def load(obj, m) :
    if m.flags :
        feature = m.flags.split()

        for f in feature :
            try :
                features.load(obj.bot, f)

            except (ImportError, KeyError) :
                obj.reply("[\x02Feature Error\x02] \"{}\" doesn't exist.".format(f), m)

            except Exception as e :
               obj.reply("[\x02Feature Error\x02 {}] {}".format(f, e), m)

@owner
def run(obj, m) :
    try :
        reply = eval(m.flags)

    except Exception as e :
        reply = "Bro, that's fucked up: {}".format(e)

    obj.reply(reply, m)

@user
def quiet(obj, m) :
    if not obj.isQuiet :
        obj.reply("Yes, master.", m)
        obj.isQuiet = True

    else :
        obj.isQuiet = False

@user
def message(obj, m) :
    p = m.flags.split(" ", 1)
    target = m.target if p[0] == "chan" else p[0]

    if len(p) > 1 :
        obj.message(target, p[1])
