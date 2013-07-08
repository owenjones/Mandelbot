#Mandelbot
def owner(commandCall) :
    def inner(obj, params) :
        print("In decorator")
        if params[1][0]["user"] == obj.config["owner"] :
            print("Can call")
            commandCall(obj, params)

        else :
            print("Can't call")
            obj.message(params[1][2], "This command can only be run by the bot owner")

    return inner


def user(commandCall) :
    def inner(obj, params) :
        if params[1][0]["user"] in obj.config["users"] or params[1][0]["user"] == obj.config["owner"] :
            commandCall(obj, params)

        else :
            obj.message(params[1][2], "This command can only be run by specified users")

    return inner
