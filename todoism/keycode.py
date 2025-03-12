import json
import curses
import time
import todoism.print as pr
import todoism.message as msg
import todoism.preference as pref


def wait_for_enter(stdscr):
    """Wait for user to press Enter key, ignore other keys"""
    while True:
        ch = stdscr.getch()
        if ch == ENTER:
            return


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

    pr.print_msg_center(stdscr, msg.keycode_msg)
    wait_for_enter(stdscr)

    restart = False

    while True:
        restart = False
        for key in key_codes:
            key_codes[key] = 0

        # Step 1: Ctrl+Left
        pr.print_msg_center(stdscr, msg.keycode_recording_ctrl_left_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            continue
        elif ch == ord('q'):
            return False
        key_codes['ctrl+left'] = ch
        pr.print_msg_center(stdscr, msg.keycode_feedback_ctrl_left_msg, 2)
        wait_for_enter(stdscr)

        # Step 2: Ctrl+Right
        pr.print_msg_center(stdscr, msg.keycode_recording_ctrl_right_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            continue
        elif ch == ord('q'):
            return False
        key_codes['ctrl+right'] = ch
        pr.print_msg_center(stdscr, msg.keycode_feedback_ctrl_right_msg, 2)
        wait_for_enter(stdscr)

        # Step 3: Ctrl+Shift+Left
        pr.print_msg_center(
            stdscr, msg.keycode_recording_ctrl_shift_left_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            continue
        elif ch == ord('q'):
            return False
        key_codes['ctrl+shift+left'] = ch
        pr.print_msg_center(
            stdscr, msg.keycode_feedback_ctrl_shift_left_msg, 2)
        wait_for_enter(stdscr)

        # Step 4: Ctrl+Shift+Right
        pr.print_msg_center(
            stdscr, msg.keycode_recording_ctrl_shift_right_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            continue
        elif ch == ord('q'):
            return False
        key_codes['ctrl+shift+right'] = ch
        pr.print_msg_center(
            stdscr, msg.keycode_feedback_ctrl_shift_right_msg, 2)
        wait_for_enter(stdscr)

        # Step 5: Alt+Left
        pr.print_msg_center(stdscr, msg.keycode_recording_alt_left_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            continue
        elif ch == ord('q'):
            return False
        key_codes['alt+left'] = ch
        pr.print_msg_center(stdscr, msg.keycode_feedback_alt_left_msg, 2)
        wait_for_enter(stdscr)

        # Step 6: Alt+Right
        pr.print_msg_center(stdscr, msg.keycode_recording_alt_right_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            continue
        elif ch == ord('q'):
            return False
        key_codes['alt+right'] = ch
        pr.print_msg_center(stdscr, msg.keycode_feedback_alt_right_msg, 2)
        wait_for_enter(stdscr)

        if restart:
            continue

        for key, code in key_codes.items():
            save_key_code(key, code)

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
