import curses
from build_game import build_game

if __name__ == '__main__':

    curses.update_lines_cols()
    curses.wrapper(build_game)
