"""
Ignore the stuff that goes on in this file, it's kind of my testing
and building area at the minute.
"""
import json

if __name__ == '__main__' :

    with open("config.json") as fp:
        conf = json.load(fp)
        print(conf)
