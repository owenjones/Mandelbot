import time
import mandelbot.utils as utils
import mandelbot.connection as conn

if __name__ == '__main__' :

    class Test(object) :
        def parse(message) :
            part = message.split(" :")
            if(part[0] == "PING") :
                n.send("PONG " + part[1] + "\r\n" )

            print(message)

    n = conn.connection("irc.awfulnet.org", 6697, True, False)
    n.handler = (Test, "parse")
    n.connect()

    time.sleep(2)
    n.send("NICK MBOTTEST\r\n")
    n.send("USER MBOT * * :MBOT\r\n")
