import queue
import curses
import sys
import logging
import screen
import irc
import time
from irc import Irc
from ircsocket import IrcSocket
from screen import Screen
import threading
import time
import threading
from serverparser import ServerParser
from exceptions import *

class Client:
    """This is the main class of the program
    Each execution of the program will have only one client
    Each client has one screen and zero or more IRC classes"""

    def parse_messages(self):
        while 1:
            command = self.buffer.get() # Blocks until new message comes in
            self.screen.put_line(ServerParser.parse_message(command))

        # while 1:
        #     # Get the latest item from the queue
        #     try:
        #         command = self.buffer.get(block=False)
        #         # Parse the command the put the line on the screen            
        #         self.screen.put_line(ServerParser.parse_message(command))
        #     except queue.Empty:
        #         pass

    def do_command(self, line):
        # TODO spinoff
        """This is a call back for screen
        It executes the command the user typed"""
        if line == "/disconnect":
            if self.irc.is_connected():
                logging.info('[Client] User requested disconnect')
                self.irc.disconnect()
            else:
                self.screen.put_line('You are not connected')
        elif line == "/connect":
            self.irc.connect()
        elif line == "/quit":
            logging.info('[Client] User requested quit')
            self.quit_signal.set() # Signals to main thread to quit
        elif line == "/easter":
            self.screen.put_line("egg")
        elif self.irc.is_connected():
            try:
                self.irc.send_raw(line)
            # except SocketTimeout:
            #     logging.warning('Socket timeout')
            except OSError as err:
                logging.warning(err)
            # except SocketNotConnected:
            #     logging.debug('socket not connected')

    def __init__(self, screenObj, quit_signal):
        """Initialize the client with a screen object"""
        # Create a signal that other threads can use to stop the program
        self.buffer = queue.SimpleQueue()
        self.screen = Screen(screenObj, self.do_command)
        self.screen.draw_screen()
        self.parse_message_thread = threading.Thread(target=self.parse_messages, daemon=True)
        self.parse_message_thread.start()
        self.quit_signal = quit_signal
        self.screen.put_line('WWWelcome to the wwwiggleVerse!!!')
        self.irc = Irc('localhost', 6667, 'cat', 'cat', 'cat', self.parse_messages, self.buffer) # TODO remove
