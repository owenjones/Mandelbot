import json

if __name__ == '__main__' :

    with open("config.json") as fp:
        conf = json.load(fp)
        print(conf)
