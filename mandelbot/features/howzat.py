# Mandelbot
"""
Howzat! (Cricket Scores)
"""
import sys, time
from threading import Timer

score = []
thread = None

def initalize(bot) :
    global thread
    bot.registerCommand("howzat", (sys.modules[__name__], "howzat"))
    thread = Timer(120, "fetcher")

def fetcher() :
    global score, thread


def howzat(obj, m) :
    global score, thread
    if m.flags and m.flags.lower in ("stop", "exit") :
        thread.stop()
        return

    if score :
        reply = score[-1:]

    else :
        reply = "[Howzat!] No Scores Recorded"

    obj.reply(reply, m)
