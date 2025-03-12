import json
import todoism.preference as pref

def set_strikethrough(enabled):
    """Set strikethrough effect for completed tasks"""
    try:
        with open(pref.settings_path, "r+") as settings_file:
            settings = json.load(settings_file)
            settings['strikethrough'] = enabled
            settings_file.seek(0)  # move pointer back to beginning
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        pref.setup_default_settings()

def get_strikethrough():
    """Get strikethrough setting state"""
    try:
        with open(pref.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return settings.get('strikethrough', True)  # Default to True if not found
    except FileNotFoundError:
        pref.setup_default_settings()
        return True