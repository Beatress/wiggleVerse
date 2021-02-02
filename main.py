#!env python

import curses
import time
from curses import wrapper

def main(screen):
    def put_line(text):
        lines.append(text)
        draw_screen()
        time.sleep(1)

    def draw_screen():
        """Wrapper function for curses refresh()
        Redisplays topic line, chat log, status bar, and input window
        """
        screen.clear()
        line = len(lines) - 1
        i = 0
        while i < (rose - 2) and i > 0 and index >= 0:
            screen.addstr(rose - 2 - i, 0, lines[line])
            i += 1
            index -= 1
        screen.refresh()

    # Main code begins here        
    screen.clear()
    screen.nodelay(True) # Makes input calls non-blocking
    rose, calls = screen.getmaxyx()
    lines = []
    top_text = 'wiggled the world'
    status_bar = 'wiggled the world'

    with open('server.log') as f:
        chat = f.readlines()

    for line in chat:
        put_line(line)

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

if __name__== "__main__":
    wrapper(main) # Wrapper takes care of set up and tear down