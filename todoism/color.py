import json
import curses
import todoism.preference as pref

color_set = {
    "blue": curses.COLOR_BLUE,
    "red": curses.COLOR_RED,
    "yellow": curses.COLOR_YELLOW,
    "green": curses.COLOR_GREEN,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
    "white": curses.COLOR_WHITE
}

def set_color_selected(color: str):
    # invalid color
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
        setup_default_settings()


def get_color_selected():
    try:
        with open(pref.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            color = settings['selected_color']
            if color == "random":
                return random.choice(list(color_set.values()))
            return color_set[color]
    except FileNotFoundError:
        setup_default_settings()
        return curses.COLOR_BLUE