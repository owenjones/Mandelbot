# Mandelbot
"""
Howzat! Cricket Scores
"""
import sys

def initalise(bot) :
    bot.registerCommand("howzat", (sys.modules[__name__], "howzat"))

def howzat(obj, flags) :
    pass
