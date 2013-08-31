# Mandelbot

"""
wiki.py - Wikipedia search

Requires:
* requests      - http://docs.python-requests.org/en/latest/
* BeautifulSoup - http://www.crummy.com/software/BeautifulSoup/
"""

import sys, urllib, string
from .. import utils
from ..__init__ import __version__, __url__

try :
    from mandelbot.lib import requests
    from mandelbot.lib.bs4 import BeautifulSoup

except ImportError as e :
    utils.log().error("[Feature Error wiki] A required module is not installed ({})".format(e))

prefix = "http://en.wikipedia.org/wiki/"
apiurl = "http://en.wikipedia.org/w/api.php"
uagent = "Mandelbot IRC Bot {} - {}".format(__version__, __url__)
length = 250

def initalize(bot) :
    bot.registerCommand("wiki", (sys.modules[__name__], "wiki"))

def wiki(obj, flags) :
    inp = flags[0]

    if inp :
        split = inp.rsplit(" ", 1)

        if (len(split) > 1) and (split[1] in string.digits) :
            term = split[0]
            offset = int(split[1]) - 1

        else :
            term = inp
            offset = 0

        result = search(term, offset)
        if result :
            url = prefix + urllib.parse.quote(result.replace(" ", "_"))
            p = {"action" : "render"}
            h = {"user-agent" : uagent}

            r = requests.get(url, params=p, headers=h)
            s = BeautifulSoup(r.text, "html.parser")
            p = s.findAll("p")[0].getText().strip("\n")

            if len(p) > length :
                formatted = "{} {}".format(p[:length].rsplit(".", 1)[0], url)

            else :
                formatted = p

            obj.reply("{}: {}".format(flags[1][0].nick, formatted), flags)

        else :
            obj.reply("{}: No results for \"{}\"".format(flags[1][0].nick, term), flags)

def search(term, offset = 0) :
    p = {"format" : "json",
         "action" : "opensearch",
         "search" : term,
         "limit"  : (offset + 1)}

    h = {"user-agent" : uagent}

    r = requests.get(apiurl, params=p, headers=h)

    results = r.json()[1]

    try :
        return results[offset]

    except IndexError :
        return False
