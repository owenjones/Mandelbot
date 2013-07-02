class MandelbotException(RuntimeError) :
    """
    "I'm sorry, I seem to have broken slightly. My apologies." ~ Mandelbot
    """

# Config

# Network
class NetworkError(MandelbotException) :
    """
    An error occurred with the IRC network.
    """

class InvalidServer(NetworkError) :
    """
    The server and/or port for this network are invalid.
     - Server must be passed as a string
     - Port must be passed as an integer
    """

class NoServerConnection(NetworkError) :
    """
    A connection to the IRC network server could not be established.
     - Check that there is an internet connection and that Mandelbot can reach the outside world
     - Check the servers are correct and online
    """

# Connection
class ConnectionError(MandelbotException) :
    """
    An error occured with the connection.
    """

class InvalidConnectionInformation(ConnectionError) :
    """
    The connection information is invalid.
     - Host must be passed as a string
     - Port must be passed as an integer
     - SSL is a boolean value
     - Blocking is a boolean value
    """

class InvalidHandler(ConnectionError) :
    """
    The response handler is invalid.
     - handler must either be a method in the connection object (and the method passed as a string)
     - or handler must be a method in the specified object (and the namespace and method passed in a tuple or list)
     - the method must exist within the object
     """

class NoSocket(ConnectionError) :
    """
    The socket being used doesn't exist.
    """

class CouldNotConnect(ConnectionError) :
    """
    Could not initiate a socket connection.
     - Check the host is correct (and online)
     - Check the port is correct (and receiving connections)
    """

class CouldNotDisconnect(ConnectionError) :
    """
    Could not properly close the socket connection.
    """

class CouldNotSend(ConnectionError) :
    """
    Could not send a message to the socket.
    """

class CouldNotReceive(ConnectionError) :
    """
    Could not receive a message from the socket.
    """

class SocketClosedUnexpectedly(ConnectionError) :
    """
    The socket closed when we weren't expecting it to.
    """