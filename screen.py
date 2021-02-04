import helpers
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

    def put_line(self, text):
        """Adds a line to the internal list of lines
        TODO: Trim and keep a scroll back
        """
        lines = textwrap.wrap(text, self.calls)
        for line in lines:
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

        line = len(self.lines) - 1
        i = 1 # Leave room for topic line
        while i < (self.rose - 2) and line >= 0:
            self.screen.addstr(self.rose - 2 - i, 0, self.lines[line],
            curses.color_pair(1))
            i += 1
            line -= 1

        # Move the cursor to correct place on input line
        # TODO: Make this dynamic
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
            end = start + self.calls - 1
        else:
            start = 0
            end = length
        try:
            self.screen.addstr(self.rose-1, 0, self.input[start:end])
        except:
            helpers.eprint(start, end, self.calls)
            
    def do_read(self):
        """Get input. This should be executed in its own thread?"""
        curses.noecho()
        c = self.screen.getch() # read a character
        if str(c) == curses.KEY_BACKSPACE or c == 127 and len(self.input) > 0:
            helpers.eprint('backspace')
            self.curs_pos -= 1
            self.input = self.input[:-1]
        
        elif str(c) == curses.KEY_ENTER or c == 10:
            helpers.eprint('enter')
            self.put_line(self.input)
            self.send_callback(self.input)
            self.input = ""
            self.curs_pos = 0

        elif curses.ascii.isprint(c):
            try:
                self.input = self.input + chr(c)
                if self.curs_pos < self.calls - 1:
                    self.curs_pos += 1
            except ValueError:
                helpers.eprint('ValueError')
                # Ignore certain special character codes for application start

        self.draw_screen()

    # pad = curses.newpad(rose * 5, calls)

    # def print_text():
    #     pad.addstr('Autem sapiente laboriosam recusandae numquam enim atque nam. Aut iure et quia quos tempore nihil. Occaecati dolor quisquam ipsam et fugit id suscipit. Ipsa iure id praesentium voluptas sint cum mollitia possimus. Aut amet nulla sed quo labore. Soluta  provident enim ut magnam in. Aspernatur commodi rerum ipsa et. Neque laboriosam aperiam ut et. Magni delectus dignissimos aut vel sapiente aut itaque sint. Laborum laudantium iusto nihil cum assumenda.')
    #     pad.addstr('Autem sapiente laboriosam recusandae numquam enim atque nam. Aut iure et quia quos tempore nihil. Occaecati dolor quisquam ipsam et fugit id suscipit. Ipsa iure id praesentium voluptas sint cum mollitia possimus. Aut amet nulla sed quo labore. Soluta  provident enim ut magnam in. Aspernatur commodi rerum ipsa et. Neque laboriosam aperiam ut et. Magni delectus dignissimos aut vel sapiente aut itaque sint. Laborum laudantium iusto nihil cum assumenda.')

    #     pad.refresh(0,0, 0,0, max_rows -1, max_cols -1 )

    # while True:
    #     c = screen.getch()
    #     if c == ord('d'):
    #         screen.addstr("Wiggle The World!")
    #     elif c == ord('q'):
    #         break
    #     elif c == ord('b'):
    #         curses.beep()
    #     elif c == ord('p'):
    #         print_text()
    #     elif c == ord('c'):
    #         screen.move(0,0)
    #     screen.refresh()
