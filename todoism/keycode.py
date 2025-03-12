import json
import curses
import time
import todoism.print as pr
import todoism.message as msg
import todoism.preference as pref

def record_key_codes(stdscr):
    """Record key codes for special key combinations"""
    curses.start_color()
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.curs_set(0)
    key_codes = {
        'ctrl+left': 0,
        'ctrl+right': 0,
        'ctrl+shift+left': 0,
        'ctrl+shift+right': 0,
        'alt+left': 0,
        'alt+right': 0
    }

    # Set timeout to non-blocking
    stdscr.timeout(-1)

    # Display welcome message
    pr.print_msg_center(stdscr, msg.keycode_msg)
    ch = stdscr.getch()
    if ch == ord('q'):
        return False
    
    # Key combination definitions
    key_definitions = [
        {
            'name': 'ctrl+left',
            'prompt_msg': msg.keycode_recording_ctrl_left_msg,
            'feedback_msg': msg.keycode_feedback_ctrl_left_msg
        },
        {
            'name': 'ctrl+right',
            'prompt_msg': msg.keycode_recording_ctrl_right_msg,
            'feedback_msg': msg.keycode_feedback_ctrl_right_msg
        },
        {
            'name': 'ctrl+shift+left',
            'prompt_msg': msg.keycode_recording_ctrl_shift_left_msg,
            'feedback_msg': msg.keycode_feedback_ctrl_shift_left_msg
        },
        {
            'name': 'ctrl+shift+right', 
            'prompt_msg': msg.keycode_recording_ctrl_shift_right_msg,
            'feedback_msg': msg.keycode_feedback_ctrl_shift_right_msg
        },
        {
            'name': 'alt+left',
            'prompt_msg': msg.keycode_recording_alt_left_msg,
            'feedback_msg': msg.keycode_feedback_alt_left_msg
        },
        {
            'name': 'alt+right',
            'prompt_msg': msg.keycode_recording_alt_right_msg,
            'feedback_msg': msg.keycode_feedback_alt_right_msg
        }
    ]

    while True:
        # Reset all key codes at start of new recording session
        for key in key_codes:
            key_codes[key] = 0
            
        restart_session = False
        
        # Process each key combination
        for key_def in key_definitions:
            key_name = key_def['name']
            
            # Show prompt message for this key
            pr.print_msg_center(stdscr, key_def['prompt_msg'], 3, 3)
            
            # Get the key code
            ch = stdscr.getch()
            
            # Handle restart/quit during key recording
            if ch == ord('r'):
                restart_session = True
                pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
                time.sleep(1)
                break
            elif ch == ord('q'):
                return False
                
            # Record the key code
            key_codes[key_name] = ch
            
            # Show feedback message
            pr.print_msg_center(stdscr, key_def['feedback_msg'], 2)
            
            # Wait for Enter to continue, or handle restart/quit
            while True:
                ch = stdscr.getch()
                if ch == ENTER:
                    break
                elif ch == ord('r'):
                    restart_session = True
                    pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
                    time.sleep(1)
                    break
                elif ch == ord('q'):
                    return False
            
            # If restart was requested during confirmation, break out of key loop
            if restart_session:
                break
        
        # If we completed all keys without restart, save and exit
        if not restart_session:
            # Save all recorded key codes
            for key, code in key_codes.items():
                save_key_code(key, code)
            
            # Show completion message
            pr.print_msg_center(stdscr, msg.keycode_completion_msg, 2)
            time.sleep(1)
            return True


def need_key_recording():
    """Check if we need to record key codes (all keys are 0)"""
    try:
        with open(pref.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return (settings.get('ctrl+shift+left', 0) == 0 and
                    settings.get('ctrl+shift+right', 0) == 0 and
                    settings.get('ctrl+left', 0) == 0 and
                    settings.get('ctrl+right', 0) == 0 and
                    settings.get('alt+left', 0) == 0 and
                    settings.get('alt+right', 0) == 0)
    except FileNotFoundError:
        pref.setup_default_settings()
        return True


def save_key_code(key_name, code):
    """Save a recorded key code to settings"""
    try:
        with open(pref.settings_path, "r+") as settings_file:
            settings = json.load(settings_file)
            settings[key_name] = code
            settings_file.seek(0)
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        pref.setup_default_settings()


def get_key_codes():
    """Get all key codes from settings"""
    try:
        with open(pref.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return {
                'ctrl+left': settings.get('ctrl+left', 0),
                'ctrl+right': settings.get('ctrl+right', 0),
                'ctrl+shift+left': settings.get('ctrl+shift+left', 0),
                'ctrl+shift+right': settings.get('ctrl+shift+right', 0),
                'alt+left': settings.get('alt+left', 0),
                'alt+right': settings.get('alt+right', 0)
            }
    except FileNotFoundError:
        pref.setup_default_settings()
        return {
            'ctrl+left': 0,
            'ctrl+right': 0,
            'ctrl+shift+left': 0,
            'ctrl+shift+right': 0,
            'alt+left': 0,
            'alt+right': 0
        }


CTRL_LEFT = 0
CTRL_RIGHT = 0
CTRL_SHIFT_LEFT = 0
CTRL_SHIFT_RIGHT = 0
ALT_LEFT = 0
ALT_RIGHT = 0
BACKSPACE = 127
ESC = 27
ENTER = 10
