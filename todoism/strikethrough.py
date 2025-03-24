import json

import todoism.preference as pref

def set_strikethrough(enabled):
    """Set strikethrough effect for completed tasks"""
    try:
        with open(pref.get_settings_path(), "r+") as settings_file:
            settings = json.load(settings_file)
            settings["strikethrough"] = enabled
            settings_file.seek(0)
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        pref.setup_default_settings()

def get_strikethrough():
    """Get strikethrough setting state"""
    try:
        with open(pref.get_settings_path(), 'r') as settings_file:
            settings = json.load(settings_file)
            return settings.get("strikethrough", True)
    except FileNotFoundError:
        pref.setup_default_settings()
        return True
    
def apply(text: str) -> str:
    if not text:
        return ""
    return ''.join(char + '\u0336' for char in text)