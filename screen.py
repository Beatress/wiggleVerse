import logging
import random
import textwrap # For wrapping lines to screen length
import curses
import curses.ascii
import ircsocket

class Screen:
    """Abstraction class for a curses screen
    Takes a screen object as parameters
    """
    def __init__(self, screenObj, send_callback):
        self.screen = screenObj
        self.rose, self.calls = self.screen.getmaxyx()
        self.lines = []
        self.top_text = 'WiggleChat v0.1' # For channel topic and other
        self.status_bar = 'Let\'s Wiggle the World!'
        self.input = ""
        self.curs_pos = 0
        self.screen.nodelay(0) # Makes input calls non-blocking
        self.send_callback = send_callback

        # create color pairs
        """
        1: Chat text
        2: Status bar text 
        3: Title bar text
        """
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLUE)

    def put_line(self, line):
        """Adds a line to the internal list of lines
        TODO: Trim and keep a scroll back
        """
        self.lines.append(line)
        self.draw_screen()

    def draw_screen(self):
        """Wrapper function for curses refresh()
        Redisplays topic line, chat log, status bar, and input window
        """
        self.screen.clear()
        self.draw_status()
        self.draw_top_text()
        self.draw_input()

        # Use a random large number as at internal way to mark where to re split lines
        # This introduces the possibility for a minor display bug extremely rarely
        # TODO find a better way to do this
        # random_number = random.randint(1111111,9999999)

        # wrapped_lines = textwrap.wrap(str(random_number).join(self.lines), self.calls)
        
        # logging.debug(wrapped_lines)
        # wrapped_lines.split(str(random_number))
        wrapped_lines = []
        for line in self.lines:
            lines = textwrap.wrap(line, self.calls)
            for line in lines:
                wrapped_lines.append(line)

        line = len(wrapped_lines) - 1
        i = 1 # Leave room for topic line
        while i < (self.rose - 2) and line >= 0:
            self.screen.addstr(self.rose - 2 - i, 0, wrapped_lines[line],
            curses.color_pair(1))
            i += 1
            line -= 1

        # Move the cursor to correct place on input line
        self.screen.move(self.rose - 1, self.curs_pos)

        self.screen.refresh()

    def draw_status(self):
        """Draws the status""" 
        # Pad status text to fill background bar
        status_bar_filled = self.status_bar + " " * (self.calls - len(self.status_bar))

        self.screen.addstr(self.rose - 2, 0, status_bar_filled[:self.calls],
        curses.color_pair(2))

    def draw_top_text(self):
        """Draws the top text
        This is usually used for the channel topic
        """ 
        # Pad top text to fill background bar
        top_bar = self.top_text + " " * (self.calls - len(self.top_text))
        self.screen.addstr(0, 0, top_bar[:self.calls],
        curses.color_pair(3))

    def draw_input(self):
        """Draws the input text
        This keeps track of the current line being typed"""
        length = len(self.input)
        if length >= self.calls:
            start = length - self.calls - 1
            end = start + self.calls
        else:
            start = 0
            end = length
        self.screen.addstr(self.rose-1, 0, self.input[start:end])
        # except:
        #     logging.debug(start, end, self.calls)
            
    def get_input(self):
        """Get input. Non blocking """
        curses.noecho()
        c = self.screen.getch() # read a character
        if str(c) == curses.KEY_BACKSPACE or c == 127 and len(self.input) > 0:
            logging.debug('backspace')
            self.curs_pos -= 1
            self.input = self.input[:-1]
        
        elif str(c) == curses.KEY_ENTER or c == 10:
            logging.debug('enter')
            self.put_line(self.input)
            self.send_callback(self.input)
            self.input = ""
            self.curs_pos = 0

        elif c == curses.KEY_RESIZE:
            # Get new dimensions
            self.rose, self.calls = self.screen.getmaxyx()

        elif curses.ascii.isprint(c):
            try:
                self.input = self.input + chr(c)
                if self.curs_pos < self.calls - 1:
                    self.curs_pos += 1
            except ValueError:
                logging.debug('ValueError')
                # Ignore certain special character codes for application start

        self.draw_screen()