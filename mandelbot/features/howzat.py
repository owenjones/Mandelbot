# Mandelbot
"""
Howzat! (Cricket Scores)
"""
import sys
from threading import Timer

score = []
thread = None

def initalise(bot) :
    global thread
    bot.registerCommand("howzat", (sys.modules[__name__], "howzat"))
    #thread = Timer(120, "fetcher")

def fetcher() :
    global score, thread

def howzat(obj, flags) :
    global score, thread
    if flags and flags[0].lower in ("stop", "exit") :
        scorethread.stop()
        return

    if score :
        reply = score[-1:]

    else :
        "[Error] No Scores Recorded"

    obj.reply(flags, reply)
