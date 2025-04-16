import os
import json

import todoism.state as st

HOME_DIR = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME_DIR, ".todoism")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(CONFIG_DIR, exist_ok=True)

SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
PURGED_FILE_PATH = os.path.join(CONFIG_DIR, "purged.json")
TASKS_FILE_PATH = os.path.join(CONFIG_DIR, "tasks.json")
CATEGORIES_FILE_PATH = os.path.join(CONFIG_DIR, "categories.json")

default_settings = {
    "date_format": "Y-M-D",
    "selected_color": "purple",
    "tag": True,
    "strikethrough": True,
    "sort_by_flagged": False,
    "sort_by_done": False,
    "bold_text": False,
    "ctrl+left": 0,
    "ctrl+right": 0,
    "ctrl+shift+left": 0,
    "ctrl+shift+right": 0,
    "alt+left": 0,
    "alt+right": 0,
    "last_update_check": 0
}

def get_tasks_file_path() -> str:
    return os.path.join(ROOT_DIR, "test/.todoism/tasks.json") if st.dev_mode else TASKS_FILE_PATH

def get_categories_file_path() -> str:
    return os.path.join(ROOT_DIR, "test/.todoism/categories.json") if st.dev_mode else CATEGORIES_FILE_PATH

def get_purged_file_path() -> str:
    return os.path.join(ROOT_DIR, "test/.todoism/purged.json") if st.dev_mode else PURGED_FILE_PATH

def get_settings_file_path() -> str:
    return os.path.join(ROOT_DIR, "test/.todoism/settings.json") if st.dev_mode else SETTINGS_PATH

def setup_default_settings():
    """
    setup default settings if no settings.json were found
    """
    
    with open(SETTINGS_PATH, 'w') as file:
        json.dump(default_settings, file, indent=4)
    return default_settings

def load_preferences():
    """
    Load settings from the settings.json file.
    If the file doesn't exist or is invalid, create a new one with default settings.
    """
    try:
        with open(SETTINGS_PATH, 'r') as file:
            preferences = json.load(file)
            st.theme_color = preferences.get("selected_color", "blue")
            st.date_format = preferences.get("date_format", "Y-M-D")
            st.sort_by_done = preferences.get("sort_by_done", False)
            st.sort_by_flagged = preferences.get("sort_by_flagged", False)
            st.tag = preferences.get("tag", True)
            st.strikethrough = preferences.get("strikethrough", True)
            st.bold_text = preferences.get("bold_text", False)
    except (FileNotFoundError, json.JSONDecodeError):
        setup_default_settings()

def update_preferences():
    """
    Update settings file with new entries when program is updated.
    This ensures backward compatibility between versions.
    """
    try:
        
        # Try to read current settings
        try:
            with open(SETTINGS_PATH, 'r') as file:
                current_settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # If settings file doesn't exist or is invalid, create default
            return setup_default_settings()
            
        # Check for missing entries and add them
        updated = False
        for key, value in default_settings.items():
            if key not in current_settings:
                current_settings[key] = value
                updated = True
                
        # Save updated settings if changes were made
        if updated:
            with open(SETTINGS_PATH, 'w') as file:
                json.dump(current_settings, file, indent=4)
                
        return current_settings
    except Exception as _:
        # If anything goes wrong, return default settings
        return setup_default_settings()
        
def set_bool_setting(setting_name: str, value: bool):
    """Set a boolean setting in the settings file."""
    try:
        with open(SETTINGS_PATH, 'r+') as settings_file:
            settings = json.load(settings_file)
            settings[setting_name] = value
            settings_file.seek(0)
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
            
    except FileNotFoundError:
        setup_default_settings()
        
def set_str_setting(setting_name: str, value: str):
    """Set a string setting in the settings file."""
    try:
        with open(SETTINGS_PATH, 'r+') as settings_file:
            settings = json.load(settings_file)
            settings[setting_name] = value
            settings_file.seek(0)
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
            
    except (FileNotFoundError, json.JSONDecodeError):
        setup_default_settings()
                    
def apply_strikethrough(text: str) -> str:
    if not text:
        return ""
    return ''.join(char + '\u0336' for char in text)