import os
import json

home_dir = os.path.expanduser("~")
config_dir = os.path.join(home_dir, ".todoism")
os.makedirs(config_dir, exist_ok=True)

settings_path = os.path.join(config_dir, "settings.json")

purged_file_path = os.path.join(config_dir, "purged.json")

tasks_file_path = os.path.join(config_dir, "tasks.json")
categories_file_path = os.path.join(config_dir, "categories.json")

test_tasks_file_path = os.path.join(config_dir, "tasks_test.json")
test_categories_file_path = os.path.join(config_dir, "categories_test.json")

def setup_default_settings():
    """
    setup default settings if no settings.json were found
    """
    default_settings = {
        "date_format": "Y-M-D",
        "scroll": True,
        "sort_by_flagged": False,
        "sort_by_done": False,
        "selected_color": "blue",
        "strikethrough": True,
        "tag": True,
        "ctrl+left": 0,
        "ctrl+right": 0,
        "ctrl+shift+left": 0,
        "ctrl+shift+right": 0,
        "alt+left": 0,
        "alt+right": 0
    }
    with open(settings_path, "w") as file:
        json.dump(default_settings, file, indent=4)
    return default_settings

def update_preferences():
    """
    Update settings file with new entries when program is updated.
    This ensures backward compatibility between versions.
    """
    try:
        # Get default settings as template
        default_settings = {
            "date_format": "Y-M-D",
            "scroll": True,
            "sort_by_flagged": False,
            "sort_by_done": False,
            "selected_color": "blue",
            "strikethrough": True,
            "tag": True,
            "ctrl+left": 0,
            "ctrl+right": 0,
            "ctrl+shift+left": 0,
            "ctrl+shift+right": 0,
            "alt+left": 0,
            "alt+right": 0
        }
        
        # Try to read current settings
        try:
            with open(settings_path, "r") as file:
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
            with open(settings_path, "w") as file:
                json.dump(current_settings, file, indent=4)
                
        return current_settings
    except Exception as e:
        # If anything goes wrong, return default settings
        return setup_default_settings()

def get_tag():
    """Get strikethrough setting state"""
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return settings.get('tag', True)
    except FileNotFoundError:
        setup_default_settings()
        return True

def set_tag(enabled):
    """Set strikethrough effect for completed tasks"""
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
        
        settings['tag'] = enabled
        
        # Write the entire file at once to avoid corruption
        with open(settings_path, "w") as settings_file:
            json.dump(settings, settings_file, indent=4)
            
    except FileNotFoundError:
        setup_default_settings()

def get_date_format():
    """Get date format setting"""
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return settings.get('date_format', "Y-M-D")  # Default to Y-M-D if not found
    except FileNotFoundError:
        setup_default_settings()
        return "Y-M-D"

def set_date_format(format_string):
    """Set date format setting"""
    if format_string not in ["Y-M-D", "D-M-Y", "M-D-Y"]:
        format_string = "Y-M-D"  # Default if invalid
        
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
        
        settings['date_format'] = format_string
        
        # Write the entire file at once to avoid corruption
        with open(settings_path, "w") as settings_file:
            json.dump(settings, settings_file, indent=4)
            
    except FileNotFoundError:
        setup_default_settings()

def get_sort_flagged():
    """Get sort flagged tasks setting"""
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return settings.get('sort_by_flagged', False)
    except FileNotFoundError:
        setup_default_settings()
        return False

def set_sort_flagged(enabled):
    """Set sort flagged tasks setting"""
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
        
        settings['sort_by_flagged'] = enabled
        
        # Write the entire file at once to avoid corruption
        with open(settings_path, "w") as settings_file:
            json.dump(settings, settings_file, indent=4)
            
    except FileNotFoundError:
        setup_default_settings()
    
def get_sort_done():
    """Get sort done tasks setting"""
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return settings.get('sort_by_done', False)
    except FileNotFoundError:
        setup_default_settings()
        return False
    
def set_sort_done(enabled):
    """Set sort done tasks setting"""
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)
        
        settings['sort_by_done'] = enabled
        
        # Write the entire file at once to avoid corruption
        with open(settings_path, "w") as settings_file:
            json.dump(settings, settings_file, indent=4)
            
    except FileNotFoundError:
        setup_default_settings()