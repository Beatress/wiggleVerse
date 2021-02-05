#!env python

import client
import curses
import logging

def main(screenObj):
    """Stub that creates a Client object"""
    # Set up logging
    # TODO add %(asctime)s back to format
    logging.basicConfig(format='[%(levelname)s] %(message)s', datefmt='%H:%M:%S',
    filename='wiggle.log', encoding='utf-8', level=logging.DEBUG)
    logging.debug('test')
    c = client.Client(screenObj)

if __name__== "__main__":
    curses.wrapper(main) # Wrapper takes care of set up and tear down