#!env python

import curses
import time
import helpers
import screen
# import irc
from ircsocket import IrcSocket
from screen import Screen
import threading

def main(screenObj):
    """Main program function
    Uses Screen and IRC objects
    """

    def send_callback(line):
        # Callback for screen
        try:
            irc.put_raw(line)
        except SocketTimeout:
            helpers.eprint('socket timeout')
        except OSError as err:
            helpers.eprint(err)
        except SocketNotConnected:
            helpers.eprint('socket not connected')

    screen = Screen(screenObj, send_callback) # create Screen object
    screen.draw_screen()
    irc = IrcSocket()

    irc.connect('localhost', 6667)
    irc.put_raw('USER cat 8 * :cat')
    irc.put_raw('NICK cat')
    irc.put_raw('JOIN #test')

    while 1:
        lines = irc.get_raw()
        for line in lines:
            screen.put_line(line)
        screen.doRead()

        

if __name__== "__main__":
    curses.wrapper(main) # Wrapper takes care of set up and tear down