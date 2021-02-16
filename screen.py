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

import logging
import random
import textwrap # For wrapping lines to screen length
import curses
import curses.ascii
import ircsocket
import threading
import time

from time import strftime

# A selection of inspiration phrases
PHRASES = ['Friends over TCP/IP', 'Better than the WWWorld WWWide WWWeb', 'Where to, pal?', "Taking frequent breaks is not only healthy, it's revolutionary!", "Don't throw away your graphics card... yet", 'That internet, I tell ya hwat', 'Chat With Kindness!', 'Pet the kitty SLOWLY in ONE direction', '*you hear some noises off in the distance*', 'Free Software under the GNU GPLv2!', '/connect chat.at.wiggleland.fun :^)', 'a Nutritious Part of a Balanced Wiggler!', 'Feed the Rush!', 'Remember to Hydrate!', 'Batteries Included!', 'Let It Go~ Let It Go~', '20% off at the WiggleCo store with code WGLVRS', "Bicycling is not only wiggly, it's eco-friendly!", 'You Are Brave!', 'You Are Strong!', 'Today Will Be a Great Day!', 'No Kids in Cages!', 'Thanks for testing wiggleVerse, Mack!', 'Change options with /set', 'Not responsible for any broken sockets', 'Jupiter says: feed cats 7 times a day', 'There is More to Life than IRC!', 'You deserve to take up space!', 'Built with only the Python Standard Library!', 'Trans Women are Women!', 'Hatsune Miku is a Diva!', 'Your Story is Valid!', 'Black Lives Matter!', 'Friendship is Magic!', 'Check the tall grass for Pokemon!', "Don't Forget to Wiggle Your Fangs Today!", 'No means No! No exceptions!', '', 'Consent is important!', 'Innovating a Dormant Protocol since 2021!', "Don't Wake Wiggler!", 'Wiggles are Good for Bodies in Motion!', 'Non-binary people are valid!', 'Thanks for testing wiggleVerse, Vespurr!', 'Send raw IRC commands with /raw', 'You Are Beautiful!', 'WiggleCo: Wiggling the World', 'You Are Valid!', 'Black Trans Lives Matter!', 'Wiggler says: sleep is good', 'Trans Men are Men!', 'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww', "The Planet Can't Wait!", 'This space semi-intentionally left blank', 'Much Better Than 0.29!', 'Join the wiggleSociety', 'Wiggle the World!', 'There is an easter egg...', 'wiggleCoin up 40% today!', 'You Are Enough!']
PAGE_SCROLL_BORDER = 1 # How many lines from the previous page are kept when doing page up and page down
MAX_SCROLLBACK = 1000 # How many lines of scrollback to store
LONG_LINE_BUFFER = 3 # How much room to leave at the right side of input box for long lines in cols

class Screen:
    """Abstraction class for a curses screen
    Takes a screen object as parameters
    """
    def __init__(self, screenObj, do_command):
        self.screen = screenObj
        self.rose, self.calls = self.screen.getmaxyx()
        self.lines = []
        self.status_bar = 'Let\'s Wiggle the World!'
        self.input = ""
        self.position = 0 # Stores how far back we are looking in scroll back
        # self.screen.nodelay(True) # (Actually) makes input calls non-blocking
        self.do_command = do_command # Callback
        # Create a thread to get input
        self.stop_thread = False # Used to stop the thread when needed
        self.input_thread = threading.Thread(target=self.get_input, daemon=True)
        self.input_thread.start()

        # create color pairs
        """
        1: Chat text
        2: Title bar text 
        3: Status bar text
        # 4: Client text
        """
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLUE)
        # curses.init_pair(4, curses.COLOR_, curses.COLOR_BLACK)

    def put_line(self, line):
        """Adds a line to the internal list of lines"""
        # We store more lines than we plan on displaying because neither a list nor a queue was ideal
        # Every five hundred lines we get rid of the oldest five hundred
        if len(self.lines) >= MAX_SCROLLBACK + 500:
            logging.debug(f'Pared lines at {len(self.lines)}')
            self.lines = self.lines[-MAX_SCROLLBACK:]
        if line != '':
            time = strftime('%H:%M')
            time = f'[{time}]'
        else:
            time = ''
        self.lines.append(f'{time}{line}')
        self.draw_screen()

    def draw_screen(self):
        """Wrapper function for curses refresh()
        Redisplays topic line, chat log, status bar, and input window
        """
        try:
            # We wrap this in a try block because if the terminal is very tiny (<4 wide) it will crash
            self.screen.clear()
            self.draw_status()
            self.draw_top_text()
            self.draw_input()

            self.wrapped_lines = []
            length = len(self.lines)
            if length >= MAX_SCROLLBACK:
                start = length - MAX_SCROLLBACK
            else:
                start = 0
            
            for line in self.lines[start:length]:
                # from_client = False # Keeps track of if the line came from client or server
                # if line[0:2] == '>>':
                #     from_client = True
                lines = textwrap.wrap(line, self.calls)
                for line in lines:
                    # if from_client and line[0:2] != '>>':
                    #     line = f'>>{line}'
                    self.wrapped_lines.append(line)

            line = len(self.wrapped_lines) - self.position - 1
            # It should not be possible to change position to this value, but we are going to play it safe anyways
            if line < 0:
                line = 0

            i = 1 # Leave room for topic line

            if len(self.wrapped_lines) >= 1:
                while i < (self.rose - 2) and line >= 0:
                    self.screen.addstr(self.rose - 2 - i, 0, self.wrapped_lines[line],
                    curses.color_pair(1))
                    i += 1
                    line -= 1

            # Move the cursor to correct place on input line
            if len(self.input) + LONG_LINE_BUFFER >= self.calls:
                curs_pos = self.calls - LONG_LINE_BUFFER
            else:
                curs_pos = len(self.input)
            self.screen.move(self.rose - 1, curs_pos)

            self.screen.refresh()

        except IndexError as e:
            logging.debug(f'IndexError: {e}') # These should all be caused by having a very small terminal
        
        except curses.error as e:
            logging.debug(f'IndexError: {e}') # Safely ignore curses errors (drawing out of bounds)

    def draw_status(self):
        """Draws the status""" 
        # Pad status text to fill background bar
        status_bar_filled = self.status_bar + " " * (self.calls - len(self.status_bar))
        if self.position != 0:
            status_bar_filled = status_bar_filled[0:-8] + '--MORE--' 

        self.screen.addstr(self.rose - 2, 0, status_bar_filled[:self.calls],
        curses.color_pair(3))

    def draw_top_text(self):
        """Draws the top text
        This is usually used for the channel topic
        """ 
        # Pad top text to fill background bar
        minutes = int(strftime('%M'))
        top_text = 'wiggleVerse 0.39 - ' + PHRASES[minutes] 
        top_bar = top_text + " " * (self.calls - len(top_text))
        self.screen.addstr(0, 0, top_bar[:self.calls],
        curses.color_pair(2))

    def draw_input(self):
        """Draws the input text
        This keeps track of the current line being typed"""
        length = len(self.input)
        if length + LONG_LINE_BUFFER >= self.calls:
            start = (length + LONG_LINE_BUFFER) - self.calls
            end = start + self.calls - 1
        else:
            start = 0
            end = length
        self.screen.addstr(self.rose-1, 0, self.input[start:end])
            
    def get_input(self):
        while not self.stop_thread:
            """Get input. Blocking for now (runs in a thread9) """
            c = self.screen.getch() # read a character

            if c == curses.KEY_BACKSPACE or c == 127 and len(self.input) > 0:
                self.input = self.input[:-1]
            
            elif c == curses.KEY_ENTER or c == 10 or c == 13:
                self.do_command(self.input)
                self.input = ""

            elif c == curses.KEY_RESIZE:
                # Get new dimensions
                self.rose, self.calls = self.screen.getmaxyx()

            elif c == curses.KEY_PPAGE: # Page up
                self.position += self.rose - 3 - PAGE_SCROLL_BORDER
                # Prevent user from going above top of scroll back
                if self.position > len(self.wrapped_lines):
                    self.position = len(self.wrapped_lines) - 1 # Set scroll back at top
                    
            elif c == curses.KEY_NPAGE: # Page down
                self.position -= self.rose - 3 - PAGE_SCROLL_BORDER
                if self.position < 0: # Prevent going past end of log
                    self.position = 0

            # Printable ASCII only for now...
            # This also helps us ignore various terminal signals
            elif curses.ascii.isprint(c):
                self.input = self.input + chr(c)

            self.draw_screen()

    def set_status(self, status):
        self.status_bar = status
