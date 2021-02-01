import curses
from curses import wrapper

def main(screen):
    # Clear screen
    screen.clear()
    screen.refresh()
    pad = curses.newpad(100,100)

    def print_text():
        max_rows, max_cols = screen.getmaxyx()
        pad.addstr('Autem sapiente laboriosam recusandae numquam enim atque nam. Aut iure et quia quos tempore nihil. Occaecati dolor quisquam ipsam et fugit id suscipit. Ipsa iure id praesentium voluptas sint cum mollitia possimus. Aut amet nulla sed quo labore. Soluta  provident enim ut magnam in. Aspernatur commodi rerum ipsa et. Neque laboriosam aperiam ut et. Magni delectus dignissimos aut vel sapiente aut itaque sint. Laborum laudantium iusto nihil cum assumenda.')
        pad.addstr('Autem sapiente laboriosam recusandae numquam enim atque nam. Aut iure et quia quos tempore nihil. Occaecati dolor quisquam ipsam et fugit id suscipit. Ipsa iure id praesentium voluptas sint cum mollitia possimus. Aut amet nulla sed quo labore. Soluta  provident enim ut magnam in. Aspernatur commodi rerum ipsa et. Neque laboriosam aperiam ut et. Magni delectus dignissimos aut vel sapiente aut itaque sint. Laborum laudantium iusto nihil cum assumenda.')
    
        pad.refresh(0,0, 0,0, max_rows -1, max_cols -1 )

    while True:
      c = screen.getch()
      if c == ord('d'):
          screen.addstr("Wiggle The World!")
      elif c == ord('q'):
          break  # Exit the while loop
      elif c == ord('b'):
          curses.beep()
      elif c == ord('p'):
          print_text()
      elif c == ord('c'):
          screen.move(0,0)
      screen.refresh()

if __name__== "__main__":
    wrapper(main)