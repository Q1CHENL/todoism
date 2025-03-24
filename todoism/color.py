import json
import curses
import random
import todoism.preference as pref

SELECTION_COLOR_PAIR_NUM = 9
BACKGROUND_COLOR_PAIR_NUM = 10

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
    "black": [8, 234]
}

def setup_color_pairs():
    for color in color_set.values():
        curses.init_pair(color[0], color[1], get_color_code_by_str("black"))
    curses.init_pair(BACKGROUND_COLOR_PAIR_NUM, get_color_code_by_str("white"), get_color_code_by_str("black"))
    curses.init_pair(SELECTION_COLOR_PAIR_NUM, get_color_code_by_str("black"), get_theme_color_curses())

def set_theme_color(color: str):
    if color not in color_set and color != "random":
        return
    try:
        with open(pref.get_settings_path(), "r+") as settings_file:
            settings = json.load(settings_file)
            settings["selected_color"] = color
            settings_file.seek(0)  # move pointer back to beginning
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        pref.setup_default_settings()

def get_theme_color_curses() -> int:
    try:
        with open(pref.get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
            color = settings["selected_color"]
            if color == "random":
                return random.choice(list(color_set.values()))
            return color_set[color][1]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        color_str = pref.setup_default_settings()["selected_color"]
        return get_color_code_by_str(color_str)
    except Exception:
        return curses.COLOR_BLUE

def get_theme_color_str() -> str:
    try:
        with open(pref.get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
            color = settings["selected_color"]
            if color == "random":
                return random.choice(list(color_set.keys()))
            return color
    except FileNotFoundError:
        pref.setup_default_settings()
        return curses.COLOR_BLUE

def get_theme_color_pair_for_text() -> int:
    return get_color_pair_by_str(get_theme_color_str())

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