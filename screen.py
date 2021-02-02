import helpers
import textwrap # For wrapping lines to screen length

class Screen:
    """Abstraction class for a curses screen
    Takes a screen object as parameters
    """
    def __init__(self, screenObj):
        self.screen = screenObj
        self.rose, self.calls = self.screen.getmaxyx()
        self.lines = []
        self.top_text = 'wiggled the world' # For channel topic and other
        self.status_bar = 'wiggled the world'
        self.screen.nodelay(True) # Makes input calls non-blocking

    def put_line(self, text):
        lines = textwrap.wrap(text, self.calls)
        for line in lines:
            self.lines.append(line)
        self.draw_screen()

    def draw_screen(self):
        """Wrapper function for curses refresh()
        Redisplays topic line, chat log, status bar, and input window
        """
        self.screen.clear()
        line = len(self.lines) - 1
        i = 1 # Leave room for topic line
        while i < (self.rose - 2) and line >= 0:
            self.screen.addstr(self.rose - 2 - i, 0, self.lines[line])
            i += 1
            line -= 1
        self.screen.refresh()

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