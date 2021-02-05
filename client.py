import curses
import logging
import screen
import irc
import time
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
        if line == "/quit":
            logging.info('User requested quit')
            self.irc.disconnect()
        elif line == "/easter":
            self.screen.put_line("egg")
        else:
            try:
                self.irc.send_raw(line)
            # except SocketTimeout:
            #     logging.warning('Socket timeout')
            except OSError as err:
                logging.warning(err)
            # except SocketNotConnected:
            #     logging.debug('socket not connected')

    def __init__(self, screenObj):
        """Initialize the client with a screen object"""
        self.screen = Screen(screenObj, self.send_callback)
        self.screen.draw_screen()
        # TODO break this out
        self.irc = Irc('localhost', 6667, 'cat', 'cat', 'cat', self.get_messages)

        # while 1: 
        while 1:
            self.screen.get_input()
            if not self.irc.is_connected():
                self.screen.put_line('Connection lost. Quitting...')
                time.sleep(2)
                break
            # else:
            #     self.screen.get_input()
    