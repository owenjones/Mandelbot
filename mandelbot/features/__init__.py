# Mandelbot
"""
Mandelbot Features

Imports all the Mandelbot features, and registers their callbacks with the bot
"""
import os

features = [feature.split(".")[0] for feature in os.listdir(os.getcwd() + "/mandelbot/features")
            if feature.endswith(".py") and feature != "__init__.py"]

def load(bot) :
    for feature in features :
        f = __import__("mandelbot.features." + feature, fromlist = [feature])
        f.initalise(bot)
        del f
