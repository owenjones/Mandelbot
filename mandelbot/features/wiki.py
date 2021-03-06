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
    from ..lib import requests
    from ..lib import bs4

except ImportError as e :
    utils.log().error("[Feature Error wiki] A required module is not installed ({})".format(e))

prefix = "http://en.wikipedia.org/wiki/"
apiurl = "http://en.wikipedia.org/w/api.php"
uagent = "Mandelbot IRC Bot {} - {}".format(__version__, __url__)
length = 250

def initalize(bot) :
    bot.registerCommand("wiki", (sys.modules[__name__], "wiki"))

def wiki(obj, m) :
    inp = m.flags

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
            s = bs4.BeautifulSoup(r.text)
            p = s.findAll("p", recursive=False)[0].getText()

            if len(p) + len(url) > length :
                p = p[:(length + len(url))].rsplit(".", 1)[0]

            obj.reply("{}: {} {}".format(m.sender.nick, p, url), m)

        else :
            obj.reply("{}: No results for \"{}\"".format(m.sender.nick, term), m)

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
