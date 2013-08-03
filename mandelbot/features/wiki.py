# Mandelbot

"""
wiki.py - Wikipedia search
Requires requests (http://docs.python-requests.org/en/latest/)
"""

import sys, urllib
from mandelbot import utils

try :
    from mandelbot.lib import requests

except ImportError :
    utils.log().error("[Feature Error] Required module \"requests\" not installed")

prefix = "http://en.wikipedia.org/wiki/"
lookup = "http://lookup.dbpedia.org/api/search/KeywordSearch"
maxLength = 250

def initalize(bot) :
    bot.registerCommand("wiki", (sys.modules[__name__], "wiki"))

def wiki(obj, flags) :
    term = flags[0]

    if term :
        p = {"QueryString" : term,
             "MaxHits"     : 1}

        h = {"accept"     : "application/json",
             "user-agent" : "Mandelbot - https://github.com/owenjones/Mandelbot"}

        r = requests.get(lookup, params=p, headers=h)

        try :
            json = r.json()["results"][0]
            title = json["label"]
            description = json["description"]

            if len(description) > maxLength :
                formatted = "{}... {}{}".format(description[:maxLength], prefix, urllib.parse.quote(title.replace(" ", "_"), safe="_"))

            else :
                formatted = description

            obj.reply("{}: {}".format(flags[1][0].nick, formatted), flags)

        except IndexError :
            obj.reply("{}: No results for \"{}\"".format(flags[1][0].nick, term), flags)
