# Mandelbot
"""
Mandelbot Features

Imports all the Mandelbot features, and registers their callbacks with the bot
"""
from mandelbot import utils
import os, sys, imp, importlib

features = [feature.split(".")[0] for feature in os.listdir(os.getcwd() + "/mandelbot/features")
            if feature.endswith(".py") and feature != "__init__.py"]

def load(bot, feature) :
    f = importlib.import_module("mandelbot.features." + feature)
    f.initalise(bot)
    sys.modules[feature] = f

def loadall(bot) :
    for feature in features :
        load(bot, feature)

def reload(bot, feature) :
    f = sys.modules[feature]
    imp.reload(f)
    f.initalise(bot)
