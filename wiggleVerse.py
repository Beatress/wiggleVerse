#!env python

import curses
import time
import helpers
import screen
from screen import Screen

def main(screenObj):
    """Main program function
    Uses Screen and IRC objects
    """

    helpers.eprint('w')
    screen = Screen(screenObj) # create Screen object
    with open('server.log') as f:
        chat = f.readlines()

    for line in chat:
        screen.put_line(line)
        time.sleep(0.2)

if __name__== "__main__":
    curses.wrapper(main) # Wrapper takes care of set up and tear down