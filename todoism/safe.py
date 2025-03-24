import curses

import todoism.color as clr

def safe_addstr(stdscr, y: int, x: int, text: str, attr=0) -> bool:
    """
    Safely add a string to the screen.
    
    Args:
        stdscr: The curses window
        y: Y coordinate
        x: X coordinate
        text: Text to print
        attr: Text attributes (optional)
        
    Returns:
        bool: True if successful, False if error occurred
    """
    try:
        if attr:
            stdscr.addstr(y, x, text, attr)
            stdscr.attroff(attr)
        else:
            bkg_color_pair = clr.get_bkg_color_pair()
            stdscr.addstr(y, x, text, bkg_color_pair)
            stdscr.attroff(bkg_color_pair)
        return True
    except curses.error:
        return False

def safe_appendstr(stdscr, text: str, attr=0) -> bool:
    """
    Safely add a string to the screen."""
    try:
        if attr:
            stdscr.addstr(text, attr)
            stdscr.attroff(attr)
        else:
            bkg_color_pair = clr.get_bkg_color_pair()
            stdscr.addstr(text, bkg_color_pair)
            stdscr.attroff(bkg_color_pair)
        return True
    except curses.error:
        return False

def safe_addch(stdscr, y: int, x: int, ch: str, attr=0) -> bool:
    """Safely add a single character to the screen."""
    try:
        if attr:
            stdscr.addch(y, x, ch, attr)
            stdscr.attroff(attr)
        else:
            bkg_color_pair = clr.get_bkg_color_pair()
            stdscr.addch(y, x, ch, bkg_color_pair)
            stdscr.attroff(bkg_color_pair)
        return True
    except curses.error:
        return False

def safe_move(stdscr, y: int, x: int) -> bool:
    """Safely move the cursor."""
    try:
        stdscr.move(y, x)
        return True
    except curses.error:
        return False
    
def safe_insstr(stdscr, y: int, x: int, text: str, attr=0) -> bool:
    """Safely insert a string at the cursor."""
    try:
        if attr:
            stdscr.insstr(y, x, text, attr)
            stdscr.attroff(attr)
        else:
            bkg_color_pair = clr.get_bkg_color_pair()
            stdscr.insstr(y, x, text, bkg_color_pair)
            stdscr.attroff(bkg_color_pair)
        return True
    except curses.error:
        return False