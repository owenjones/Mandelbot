#Mandelbot
def owner(commandCall) :
    def inner(obj, m, *args) :
        if m.sender.user == obj.config["owner"] :
            commandCall(obj, m, *args)
    return inner


def user(commandCall) :
    def inner(obj, m, *args) :
        if m.sender.user in obj.config["users"] or m.sender.user == obj.config["owner"] :
            commandCall(obj, m, *args)
    return inner
