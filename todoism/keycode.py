import json
import curses
import time
import todoism.print as pr
import todoism.message as msg
import todoism.task as tsk

def record_key_codes(stdscr):
    """Record key codes for special key combinations"""
    # Set up colors
    curses.start_color()
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    key_codes = {
        'ctrl+left': 0,
        'ctrl+right': 0,
        'ctrl+shift+left': 0,
        'ctrl+shift+right': 0
    }

    # Set timeout to non-blocking
    stdscr.timeout(-1)

    pr.print_msg_center(stdscr, msg.keycode_msg)
    stdscr.getch()

    restart = False

    while True:
        restart = False
        # Reset key codes if restarting
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
            return False  # Quit without saving
        key_codes['ctrl+left'] = ch
        pr.print_msg_center(stdscr, msg.keycode_feedback_ctrl_left_msg, 2)
        stdscr.getch()

        # Step 2: Ctrl+Right
        pr.print_msg_center(stdscr, msg.keycode_recording_ctrl_right_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            break
        elif ch == ord('q'):
            return False  # Quit without saving
        key_codes['ctrl+right'] = ch
        pr.print_msg_center(stdscr, msg.keycode_feedback_ctrl_right_msg, 2)
        stdscr.getch()

        # Step 3: Ctrl+Shift+Left
        pr.print_msg_center(stdscr, msg.keycode_recording_ctrl_shift_left_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            break
        elif ch == ord('q'):
            return False  # Quit without saving
        key_codes['ctrl+shift+left'] = ch
        pr.print_msg_center(stdscr, msg.keycode_feedback_ctrl_shift_left_msg, 2)
        stdscr.getch()

        # Step 4: Ctrl+Shift+Right
        pr.print_msg_center(stdscr, msg.keycode_recording_ctrl_shift_right_msg, 3, 3)
        ch = stdscr.getch()
        if ch == ord('r'):
            restart = True
            pr.print_msg_center(stdscr, msg.keycode_restart_msg, 3)
            time.sleep(1)
            break
        elif ch == ord('q'):
            return False  # Quit without saving
        key_codes['ctrl+shift+right'] = ch
        pr.print_msg_center(stdscr, msg.keycode_feedback_ctrl_shift_right_msg, 2)
        stdscr.getch()

        if restart:
            continue

        # Show summary with actual key codes
        pr.print_msg_center(stdscr, msg.keycode_summary_msg)
        ch = stdscr.getch()

        if ch == ord('r'):
            continue  # Restart the whole process

        # Save all key codes
        for key, code in key_codes.items():
            save_key_code(key, code)

        # Show completion message
        pr.print_msg_center(stdscr, msg.keycode_completion_msg, 2)
        time.sleep(1.5)
        return True


def need_key_recording():
    """Check if we need to record key codes (all keys are 0)"""
    try:
        with open(tsk.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return (settings.get('ctrl+shift+left', 0) == 0 and
                    settings.get('ctrl+shift+right', 0) == 0 and
                    settings.get('ctrl+left', 0) == 0 and
                    settings.get('ctrl+right', 0) == 0)
    except FileNotFoundError:
        setup_default_settings()
        return True


def save_key_code(key_name, code):
    """Save a recorded key code to settings"""
    try:
        with open(tsk.settings_path, "r+") as settings_file:
            settings = json.load(settings_file)
            settings[key_name] = code
            settings_file.seek(0)
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        setup_default_settings()


def get_key_codes():
    """Get all key codes from settings"""
    try:
        with open(tsk.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            return {
                'ctrl+left': settings.get('ctrl+left', 0),
                'ctrl+right': settings.get('ctrl+right', 0),
                'ctrl+shift+left': settings.get('ctrl+shift+left', 0),
                'ctrl+shift+right': settings.get('ctrl+shift+right', 0)
            }
    except FileNotFoundError:
        setup_default_settings()
        return {'ctrl+left': 0, 'ctrl+right': 0, 'ctrl+shift+left': 0, 'ctrl+shift+right': 0}
