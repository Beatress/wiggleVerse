# Significant inspiration taken from https://github.com/chad-steadman/python-irc-client/blob/master/ircsocket.py
# Thanks Chad!

import socket
import helpers

ENCODING = 'UTF-8'       # The method for encoding and decoding all messages (UTF-8 allows 4 bytes max per char)
LINE_ENDINGS = '\r\n'    # This is appended to all messages sent by the socket (should always be CRLF)
CONNECTION_TIMEOUT = 30  # The socket will timeout after this many seconds when trying to initialize the connection
RECV_TIMEOUT = 180       # The socket will timeout after this many seconds when trying to receive data
SEND_TIMEOUT = 30        # The socket will timeout after this many seconds when trying to send data
MAX_RECV_BYTES = 4096    # The maximum amount of bytes to be received by the socket at a time

class IrcSocket:
    """This class is designed to be used by the IRC wrapper class
    """

    def __init__(self):
        """Basic initialization of the socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self, host, port):
        """Connects to an IRC server"""
        if self.connected:
            raise SocketAlreadyConnected

        self.socket.settimeout(CONNECTION_TIMEOUT)
        # Attempt to make the connection
        try:
            self.socket.connect((host, port))

        except socket.timeout:
            raise SocketTimeout

        except OSError as err:
            error_message = 'Connection failed: {}'.format(err)
            raise OSError(error_message)

        else: # Connection Successful!
            self.connected = True
            return True

    def disconnect(self):
        """Attempt to cleanly close the socket"""
        self.connected = False

        try:
            self.socket.shutdown()








class SocketAlreadyConnected(OSError):
    def __init__(self, message='A duplicate connection attempt was made', errors=None):
        super().__init__(message, errors)

class SocketTimeout(OSError):
    def __init__(self, message='Connection failed: Socket timed out', errors=None):
        super().__init__(message, errors)