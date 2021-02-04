import curses
import helpers
import screen
import irc
from irc import Irc
from ircsocket import IrcSocket
from screen import Screen
import threading
from exceptions import *

class Client:
    """This is the main class of the program
    Each execution of the program will have only one client
    Each client has one screen and zero or more IRC classes"""

    def get_messages(self, lines):
        for line in lines:
            self.screen.put_line(line)

    def send_callback(self, line):
        # Callback for screen
        try:
            self.irc.send_raw(line)
        # except SocketTimeout:
        #     helpers.eprint('socket timeout')
        except OSError as err:
            helpers.eprint(err)
        # except SocketNotConnected:
        #     helpers.eprint('socket not connected')

    def __init__(self, screenObj):
        """Initialize the client with a screen object"""
        self.screen = Screen(screenObj, self.send_callback)
        self.screen.draw_screen()
        # TODO break this out
        self.irc = Irc('localhost', 6667, 'cat', 'cat', 'cat', self.get_messages)

        while 1: 
            self.screen.get_input()
    