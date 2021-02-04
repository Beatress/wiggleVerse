#!env python

import curses
import time
import helpers
import screen
import irc
from irc import Irc
from ircsocket import IrcSocket
from screen import Screen
import threading

def main(screenObj):
    """Main program function
    Uses Screen and IRC objects
    """

    def get_messages(lines):
        for line in lines:
            screen.put_line(line)

    def send_callback(line):
        # Callback for screen
        try:
            irc.send_raw(line)
        # except SocketTimeout:
        #     helpers.eprint('socket timeout')
        except OSError as err:
            helpers.eprint(err)
        # except SocketNotConnected:
            # helpers.eprint('socket not connected')

    screen = Screen(screenObj, send_callback) # create Screen object
    screen.draw_screen()
    irc = Irc('localhost', 6667, 'cat', 'cat', 'cat', get_messages)

    while 1:
        screen.doRead()

if __name__== "__main__":
    curses.wrapper(main) # Wrapper takes care of set up and tear down