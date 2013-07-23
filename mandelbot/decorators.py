#Mandelbot
def owner(commandCall) :
    def inner(obj, params, *args) :
        if params[1][0].user == obj.config["owner"] :
            commandCall(obj, params, *args)
    return inner


def user(commandCall) :
    def inner(obj, params, *args) :
        if params[1][0].user in obj.config["users"] or params[1][0].user == obj.config["owner"] :
            commandCall(obj, params, *args)
    return inner
