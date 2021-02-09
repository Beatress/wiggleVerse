# Significant inspiration taken from https://github.com/chad-steadman/python-irc-client/blob/master/ircsocket.py
# Thanks Chad!

import socket
import logging
import asyncio
from exceptions import *

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

        except OSError as err:
            error_message = f"Connection failed: {err}"
            raise OSError(error_message)

        else: # Connection Successful!
            self.connected = True
            return True

    def disconnect(self):
        """Attempt to cleanly close the socket"""
        self.connected = False
        logging.info('Shutdown requested')

        try:
            self.socket.shutdown(socket.SHUT_RDWR)

        except OSError as err:
            logging.info('Socket not closed cleanly')

        finally: # Run clean up code
            self.cleanup()

    def cleanup(self):
        logging.debug('Running socket clean up code')            
        self.socket.close()

    def put_raw(self, text):
        """Attempts to send a raw command to the server"""
        if not self.connected:
            raise SocketNotConnected

        if text == '':
            return True

        message = f"{text}{LINE_ENDINGS}".encode(ENCODING)

        self.socket.settimeout(SEND_TIMEOUT)

        # Send until all bytes are sent or a timeout or error occurs
        try:
            bytes_sent = self.socket.sendall(message)

        except socket.timeout:
            raise SocketTimeout

        except OSError as err:
            error_message = f"Send failed: {err}"
            raise OSError(error_message)

        else:
            # If send works but returns 0 bytes, the connection was terminated
            if bytes_sent == 0:
                self.connected = False
                self.cleanup()
                raise SocketConnectionBroken
        logging.debug('Sent successfully')

    def get_raw(self): 
        """Attempts to receive data from the IRC server
        Returns a list of lines"""
        if not self.connected:
            raise SocketNotConnected

        try:
            self.socket.settimeout(RECV_TIMEOUT)
            data = self.socket.recv(MAX_RECV_BYTES)

        except socket.timeout:
            raise SocketTimeout

        except OSError as err:
            error_message = f"Receive failed: {err}"
            raise OSError(error_message)

        else: # We succeeded in receiving data
            # If recv works but returns 0 bytes, the connection was terminated
            if data == b'': # 
                raise SocketConnectionBroken

            text = data.decode(ENCODING)
            lines = text.split(LINE_ENDINGS)

            return lines