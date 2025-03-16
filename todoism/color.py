import json
import curses
import random
import todoism.preference as pref

backgournd_color_pair_num = 9

# Rainbow order
color_set = {
    # str: [self defined pair_index, curses.color]
    "red": [1, curses.COLOR_RED],
    "yellow": [2, curses.COLOR_YELLOW],
    "green": [3, curses.COLOR_GREEN],
    "cyan": [4, curses.COLOR_CYAN],
    "blue": [5, curses.COLOR_BLUE],
    "magenta": [6, curses.COLOR_MAGENTA],
    "white": [7, curses.COLOR_WHITE],
    "black": [8, curses.COLOR_BLACK]
}

def setup_color_pairs():
    for color in color_set.values():
        # For text
        curses.init_pair(color[0], color[1], curses.COLOR_BLACK)
    # For selection background
    curses.init_pair(backgournd_color_pair_num, curses.COLOR_BLACK, get_theme_color_curses())

def set_theme_color(color: str):
    if color not in color_set and color != "random":
        return
    try:
        with open(pref.settings_path, "r+") as settings_file:
            settings = json.load(settings_file)
            settings['selected_color'] = color
            settings_file.seek(0)  # move pointer back to beginning
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        pref.setup_default_settings()


def get_theme_color_curses() -> int:
    try:
        with open(pref.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            color = settings['selected_color']
            if color == "random":
                return random.choice(list(color_set.values()))
            return color_set[color][1]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return pref.setup_default_settings()['selected_color']
    except Exception:
        return curses.COLOR_BLUE


def get_theme_color_str() -> str:
    try:
        with open(pref.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            color = settings['selected_color']
            if color == "random":
                return random.choice(list(color_set.keys()))
            return color
    except FileNotFoundError:
        pref.setup_default_settings()
        return curses.COLOR_BLUE

def get_theme_color_pair_num_text() -> int:
    return color_set[get_theme_color_str()][0]
    
def get_color_pair_num_by_str_text(color: str) -> int:
    return color_set[color][0]
