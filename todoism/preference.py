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

def set_strikethrough(enabled):
    """Set strikethrough effect for completed tasks"""
    try:
        with open(settings_path, "r+") as settings_file:
            settings = json.load(settings_file)
            settings['strikethrough'] = enabled
            settings_file.seek(0)  # move pointer back to beginning
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        setup_default_settings()

def get_strikethrough():
    """Get strikethrough setting state"""
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return settings.get('strikethrough', True)  # Default to True if not found
    except FileNotFoundError:
        setup_default_settings()
        return True