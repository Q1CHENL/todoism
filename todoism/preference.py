import os
import json

import todoism.state as st

HOME_DIR = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME_DIR, ".todoism")
os.makedirs(CONFIG_DIR, exist_ok=True)

SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
PURGED_FILE_PATH = os.path.join(CONFIG_DIR, "purged.json")
TASKS_FILE_PATH = os.path.join(CONFIG_DIR, "tasks.json")
CATEGORIES_FILE_PATH = os.path.join(CONFIG_DIR, "categories.json")

TEST_SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings_test.json")
TEST_PURGED_FILE_PATH = os.path.join(CONFIG_DIR, "purged_test.json")
TEST_TASKS_FILE_PATH = os.path.join(CONFIG_DIR, "tasks_test.json")
TEST_CATEGORIES_FILE_PATH = os.path.join(CONFIG_DIR, "categories_test.json")

default_settings = {
    "date_format": "Y-M-D",
    "selected_color": "purple",
    "tag": True,
    "strikethrough": True,
    "sort_by_flagged": False,
    "sort_by_done": False,
    "ctrl+left": 0,
    "ctrl+right": 0,
    "ctrl+shift+left": 0,
    "ctrl+shift+right": 0,
    "alt+left": 0,
    "alt+right": 0
}

def get_tasks_path():
    return TEST_TASKS_FILE_PATH if st.is_dev_mode else TASKS_FILE_PATH

def get_categories_path():
    return TEST_CATEGORIES_FILE_PATH if st.is_dev_mode else CATEGORIES_FILE_PATH

def get_purged_path():
    return TEST_PURGED_FILE_PATH if st.is_dev_mode else PURGED_FILE_PATH

def get_settings_path():
    return TEST_SETTINGS_PATH if st.is_dev_mode else SETTINGS_PATH

def setup_default_settings():
    """
    setup default settings if no settings.json were found
    """
    
    with open(get_settings_path(), 'w') as file:
        json.dump(default_settings, file, indent=4)
    return default_settings

def update_preferences():
    """
    Update settings file with new entries when program is updated.
    This ensures backward compatibility between versions.
    """
    try:
        
        # Try to read current settings
        try:
            with open(get_settings_path(), 'r') as file:
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
            with open(get_settings_path(), 'w') as file:
                json.dump(current_settings, file, indent=4)
                
        return current_settings
    except Exception as e:
        # If anything goes wrong, return default settings
        return setup_default_settings()

def get_tag():
    """Get strikethrough setting state"""
    try:
        with open(get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
            return settings.get("tag", True)
    except FileNotFoundError:
        setup_default_settings()
        return True

def set_tag(enabled):
    """Set strikethrough effect for completed tasks"""
    try:
        with open(get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
        
        settings["tag"] = enabled
        
        # Write the entire file at once to avoid corruption
        with open(get_settings_path(), 'w') as settings_file:
            json.dump(settings, settings_file, indent=4)
            
    except FileNotFoundError:
        setup_default_settings()

def get_date_format():
    """Get date format setting"""
    try:
        with open(get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
            return settings.get('date_format', "Y-M-D")
    except FileNotFoundError:
        setup_default_settings()
        return "Y-M-D"

def set_date_format(format_string):
    """Set date format setting"""
    if format_string not in ["Y-M-D", "D-M-Y", "M-D-Y"]:
        format_string = "Y-M-D"

    try:
        with open(get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
        
        settings['date_format'] = format_string
        
        # Write the entire file at once to avoid corruption
        with open(get_settings_path(), 'w') as settings_file:
            json.dump(settings, settings_file, indent=4)
            
    except FileNotFoundError:
        setup_default_settings()

def get_sort_by_flagged():
    """Get sort flagged tasks setting"""
    try:
        with open(get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
            return settings.get('sort_by_flagged', False)
    except FileNotFoundError:
        setup_default_settings()
        return False

def set_sort_by_flagged(enabled):
    """Set sort flagged tasks setting"""
    try:
        with open(get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
        
        settings['sort_by_flagged'] = enabled
        
        # Write the entire file at once to avoid corruption
        with open(get_settings_path(), 'w') as settings_file:
            json.dump(settings, settings_file, indent=4)
            
    except FileNotFoundError:
        setup_default_settings()
    
def get_sort_by_done():
    """Get sort done tasks setting"""
    try:
        with open(get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
            return settings.get('sort_by_done', False)
    except FileNotFoundError:
        setup_default_settings()
        return False
    
def set_sort_by_done(enabled):
    """Set sort done tasks setting"""
    try:
        with open(get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
        
        settings['sort_by_done'] = enabled
        
        # Write the entire file at once to avoid corruption
        with open(get_settings_path(), 'w') as settings_file:
            json.dump(settings, settings_file, indent=4)
            
    except FileNotFoundError:
        setup_default_settings()
              