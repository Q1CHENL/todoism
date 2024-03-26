import json
import curses
import todoism.task as tsk

color_set = {
    "blue": curses.COLOR_BLUE,
    "red": curses.COLOR_RED,
    "yellow": curses.COLOR_YELLOW,
    "green": curses.COLOR_GREEN
}

def set_color_selected(color: str):
    # invalid color
    if color not in color_set:
        return
    try:
        with open(tsk.settings_path, "r+") as settings_file:
            settings = json.load(settings_file)
            settings['task_highlighting_color'] = color
            settings_file.seek(0)  # move pointer back to beginning
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        setup_default_settings()


def get_color_selected():
    try:
        with open(tsk.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            color = settings['task_highlighting_color']
            return color_set[color]
    except FileNotFoundError:
        setup_default_settings()
        return curses.COLOR_BLUE


def setup_default_settings():
    """
    setup default settings if no settings.json were found
    """
    default_settings = {
        "date_format": "Y-M-D",
        "scroll": True,
        "autosort_f": False,
        "autosort_d": False,
        "task_highlighting_color": "blue"
    }
    with open(tsk.settings_path, "w") as file:
        json.dump(default_settings, file, indent=4)
    return default_settings