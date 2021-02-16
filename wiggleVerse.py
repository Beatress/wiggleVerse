#!env python

import client
import curses
import logging
import threading

def main(screenObj):
    """Stub that creates a Client object"""
    # Set up logging
    logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S',
    filename='wiggle.log', level=logging.INFO)
    logging.info('[START] ***Into the wiggleVerse we go...***')
    # Puts Client into a thread
    quit_signal = threading.Event()
    c = threading.Thread(target=client.Client, args=(screenObj, quit_signal, ))
    c.start()
    quit_signal.wait() # Blocks until Client is ready to quit
    logging.info('[END] ***... and out we come***') 


if __name__== "__main__":
    curses.wrapper(main) # Wrapper takes care of set up and tear down