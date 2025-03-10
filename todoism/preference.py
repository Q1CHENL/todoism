import os
import json
import curses
import random
import todoism.task as tsk

home_dir = os.path.expanduser("~")
config_dir = os.path.join(home_dir, ".todoism")
os.makedirs(config_dir, exist_ok=True)
tasks_file_path = os.path.join(config_dir, "tasks.json")
purged_file_path = os.path.join(config_dir, "purged.json")
test_file_path = os.path.join(config_dir, "test.json")
settings_path = os.path.join(config_dir, "settings.json")
categories_file_path = os.path.join(config_dir, "categories.json")

def setup_default_settings():
    """
    setup default settings if no settings.json were found
    """
    default_settings = {
        "date_format": "Y-M-D",
        "scroll": True,
        "autosort_f": False,
        "autosort_d": False,
        "selected_color": "blue",
        "strikethrough": True,
        "ctrl+shift+left": 0,
        "ctrl+shift+right": 0,
        "ctrl+left": 0,
        "ctrl+right": 0
    }
    with open(settings_path, "w") as file:
        json.dump(default_settings, file, indent=4)
    return default_settings