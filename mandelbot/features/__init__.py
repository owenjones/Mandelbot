# Mandelbot
"""
Mandelbot Features
"""
from .. import utils
import os, sys, imp, importlib

features = []

def listFeatures() :
    """Lists all the features in the features directory"""
    global features
    features = [feature.split(".")[0] for feature in os.listdir(os.path.abspath(__file__)[:-11])
                if feature.endswith(".py") and feature != "__init__.py"]

def load(bot, feature) :
    """Loads a single Mandelbot feature"""
    try :
        f = sys.modules[feature]

    except KeyError :
        f = False

    if f :
        imp.reload(f)
        initalize(bot, f)

    else :
        f = importlib.import_module("mandelbot.features." + feature)
        initalize(bot, f)
        sys.modules[feature] = f

def loadall(bot) :
    """Loads all the Mandelbot features"""
    for feature in features :
        load(bot, feature)

def initalize(bot, feature) :
    """Initalises a Mandelbot feature"""
    try :
        feature.initalize(bot)

    except Exception as e :
        utils.log().error("[Feature Error {}] Error Loading Feature {}".format(feature, e))

listFeatures()
