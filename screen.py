import logging
import random
import textwrap # For wrapping lines to screen length
import curses
import curses.ascii
import ircsocket
import threading

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
        self.top_text = 'WiggleChat v0.39' # For channel topic and other
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
        2: Status bar text 
        3: Title bar text
        """
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLUE)

    def put_line(self, line):
        """Adds a line to the internal list of lines"""
        # We store more lines than we plan on displaying because neither a list nor a queue was ideal
        # Every five hundred lines we get rid of the oldest five hundred
        if len(self.lines) >= MAX_SCROLLBACK + 500:
            self.lines = self.lines[-MAX_SCROLLBACK:]
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
        if len(self.input) + LONG_LINE_BUFFER >= self.calls:
            curs_pos = self.calls - LONG_LINE_BUFFER
        else:
            curs_pos = len(self.input)
        self.screen.move(self.rose - 1, curs_pos)

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
                logging.debug(f"[SCREEN] {self.input}")
                self.do_command(self.input)
                self.input = ""

            elif c == curses.KEY_RESIZE:
                # Get new dimensions
                self.rose, self.calls = self.screen.getmaxyx()

            # Printable ASCII only for now...
            # This also helps us ignore various terminal signals
            elif curses.ascii.isprint(c):
                self.input = self.input + chr(c)

            self.draw_screen()
