import json
import curses

import todoism.state as st
import todoism.preference as pref

SELECTION_COLOR_PAIR_NUM = 100
BACKGROUND_COLOR_PAIR_NUM = 101

# Rainbow order
color_set = {
    # str: [self defined pair_index, color code]
    "red": [1, 196],
    "yellow": [2, 226],
    "green": [3, 41],
    "cyan": [4, 37],
    "blue": [5, 39],
    "purple": [6, 141],
    "white": [7, 231],
    "black": [8, 234],
    "grey": [9, 244]
}

def setup_color_pairs():
    for color in color_set.values():
        curses.init_pair(color[0], color[1], get_color_code_by_str("black"))
    curses.init_pair(BACKGROUND_COLOR_PAIR_NUM, get_color_code_by_str("white"), get_color_code_by_str("black"))
    curses.init_pair(SELECTION_COLOR_PAIR_NUM, get_color_code_by_str("black"), get_theme_color_curses())

def get_theme_color_curses() -> int:
    try:
        with open(pref.SETTINGS_PATH, 'r') as settings_file:
            settings = json.load(settings_file)
            color = settings["selected_color"]
            if color not in color_set:
                color = "blue"
            return color_set[color][1]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        color_str = pref.setup_default_settings()["selected_color"]
        return get_color_code_by_str(color_str)
    except Exception:
        return curses.COLOR_BLUE

def get_theme_color_pair_for_text() -> int:
    return get_color_pair_by_str(st.theme_color)

def get_theme_color_pair_for_selection() -> int:
    curses.init_pair(SELECTION_COLOR_PAIR_NUM, get_color_code_by_str("black"), get_theme_color_curses())
    return curses.color_pair(SELECTION_COLOR_PAIR_NUM)

def get_color_pair_by_str(color: str) -> int:
    return curses.color_pair(get_color_pair_num_by_str(color))

def get_color_pair_num_by_str(color: str) -> int:
    return color_set[color][0]
    
def get_bkg_color_pair() -> int:
    return curses.color_pair(BACKGROUND_COLOR_PAIR_NUM)

def get_color_code_by_str(color: str) -> int:
    return color_set[color][1]

def get_dimmed_color_code(color_code):
    """
    Get a dimmed version of a 256-color code.
    
    For colors in the 6x6x6 color cube (16-231), reduces RGB intensity.
    For grayscale colors (232-255), shifts toward darker gray.
    For standard colors (0-15), returns a darker equivalent.
    
    Args:
        color_code (int): The original 256-color code (0-255)
        
    Returns:
        int: A dimmed version of the color code
    """
    # Handle standard ANSI colors (0-15)
    if color_code < 16:
        # Map bright colors to their dark counterparts
        if color_code >= 8:
            return color_code - 8
        return color_code  # Already dark
        
    # Handle grayscale colors (232-255)
    elif color_code >= 232:
        # Move 2 steps darker but not below black
        return max(232, color_code - 4)
        
    # Handle color cube (16-231)
    else:
        # Extract RGB components (each 0-5)
        r = (color_code - 16) // 36
        g = ((color_code - 16) % 36) // 6
        b = (color_code - 16) % 6
        
        # Reduce intensity of each component (ensures values don't go below 0)
        dim_r = max(0, r - 1)
        dim_g = max(0, g - 1)
        dim_b = max(0, b - 1)
        
        # Convert back to color code
        return 16 + 36 * dim_r + 6 * dim_g + dim_b

def get_dimmed_color_pair(color_str, pair_num=None):
    """
    Get a color pair with the dimmed version of the specified color.
    
    Args:
        color_str (str): The color name to get from color_set
        pair_num (int, optional): Custom pair number to use. If None, uses a high number.
        
    Returns:
        int: Color pair attribute for the dimmed color
    """
    if color_str not in color_set:
        return 0
        
    original_code = color_set[color_str][1]
    dimmed_code = get_dimmed_color_code(original_code)
    
    # Use a high pair number to avoid conflicts
    if pair_num is None:
        pair_num = 200 + color_set[color_str][0]
        
    curses.init_pair(pair_num, dimmed_code, get_color_code_by_str("black"))
    return curses.color_pair(pair_num)
