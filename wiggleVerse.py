#!env python

# Copyright Beatrice Tohni 2021
""" This file is part of wiggleVerse.

    wiggleVerse is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    wiggleVerse is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with wiggleVerse.  If not, see <https://www.gnu.org/licenses/>."""

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
