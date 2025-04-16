import subprocess
import shutil
import sys
import time
import pyautogui
import os
import json
import psutil

# --- Configuration ---
TASK_TEXT = "Clean the kitchen"
# Replace dangerous rm -rf with a safer Python cleanup script
TODOISM_COMMAND = "python3 -c \"import shutil, os; target='test/.todoism'; print(f'Safely cleaning {target}'); [os.remove(os.path.join(target, f)) for f in os.listdir(target) if os.path.isfile(os.path.join(target, f))]\" && python3 test/generate.py && python3 -m todoism --dev; exec zsh"
TODOISM_LAUNCH_WAIT = 2
KEY_DELAY = 0.2
ACTION_DELAY = 0.5
POST_TASK_VIEW_DELAY = 2.0

# --- Special Key Handling ---
def get_special_key_codes():
    """Get the special key codes from the settings file"""
    try:
        # First try the dev mode location
        settings_path = os.path.join("test", ".todoism", "settings.json")
        if not os.path.exists(settings_path):
            # If not found, try the user's home directory
            settings_path = os.path.expanduser("~/.todoism/settings.json")
        
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                return {
                    'ctrl_left': settings.get("ctrl+left", 0),
                    'ctrl_right': settings.get("ctrl+right", 0),
                    'ctrl_shift_left': settings.get("ctrl+shift+left", 0),
                    'ctrl_shift_right': settings.get("ctrl+shift+right", 0),
                    'alt_left': settings.get("alt+left", 0),
                    'alt_right': settings.get("alt+right", 0)
                }
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Warning: Could not load key codes from settings: {e}")
    
    # Return defaults if we couldn't load from settings
    return {'ctrl_left': 0, 'ctrl_right': 0, 'ctrl_shift_left': 0, 
            'ctrl_shift_right': 0, 'alt_left': 0, 'alt_right': 0}

def emulate_special_key(key_name):
    """Emulate a special key combination using the key code"""
    key_codes = get_special_key_codes()
    code = key_codes.get(key_name, 0)
    
    if code == 0:
        print(f"⚠️ Warning: No key code found for {key_name}, using fallback")
        # Fallback to standard PyAutoGUI key combinations
        if key_name == 'ctrl_left':
            pyautogui.hotkey('ctrl', 'left')
        elif key_name == 'ctrl_right':
            pyautogui.hotkey('ctrl', 'right')
        elif key_name == 'ctrl_shift_left':
            pyautogui.hotkey('ctrl', 'shift', 'left')
        elif key_name == 'ctrl_shift_right':
            pyautogui.hotkey('ctrl', 'shift', 'right')
        elif key_name == 'alt_left':
            pyautogui.hotkey('alt', 'left')
        elif key_name == 'alt_right':
            pyautogui.hotkey('alt', 'right')
    else:
        # If we have a key code, use it directly
        print(f"🔑 Sending special key {key_name} with code {code}")
        pyautogui.press(str(code))

# --- Keycode Recording Logic ---
def handle_keycode_recording():
    """Handle the keycode recording sequence if it appears"""
    print("🔑 Checking if keycode recording is needed...")
    
    # First wait for the main screen to appear
    time.sleep(TODOISM_LAUNCH_WAIT)
    
    # The welcome screen for keycode recording will appear if needed
    # Press Enter to start the process
    focus_window()
    print("🔑 Pressing Enter to start keycode recording (if needed)")
    pyautogui.press('enter')
    time.sleep(ACTION_DELAY)
    
    # For each of the 6 key combinations, we need to:
    # 1. Press the key combination
    # 2. Press Enter to confirm
    key_combinations = [
        ('ctrl_left', ['ctrl', 'left']),
        ('ctrl_right', ['ctrl', 'right']),
        ('ctrl_shift_left', ['ctrl', 'shift', 'left']),
        ('ctrl_shift_right', ['ctrl', 'shift', 'right']),
        ('alt_left', ['alt', 'left']),
        ('alt_right', ['alt', 'right'])
    ]
    
    for name, keys in key_combinations:
        focus_window()
        print(f"🔑 Emulating {name} key combination")
        pyautogui.hotkey(*keys)
        time.sleep(KEY_DELAY)
        
        focus_window()
        print("🔑 Pressing Enter to confirm")
        pyautogui.press('enter')
        time.sleep(ACTION_DELAY)
    
    # Short delay to let the completion message display
    time.sleep(2)
    
    print("✅ Keycode recording complete")

# --- Supported Terminals ---
TERMINALS = [
    ("gnome-terminal", ["gnome-terminal", "--title=todoism-dev", "--", "zsh", "-c", "TODOISM_COMMAND"]),
    ("kitty", ["kitty", "-T", "todoism-dev", "zsh", "-c", "TODOISM_COMMAND"]),
    ("alacritty", ["alacritty", "-t", "todoism-dev", "-e", "zsh", "-c", "TODOISM_COMMAND"]),
    ("xterm", ["xterm", "-T", "todoism-dev", "-e", "zsh", "-c", "TODOISM_COMMAND"]),
    ("konsole", ["konsole", "--new-tab", "-p", "tabtitle=todoism-dev", "-e", "zsh", "-c", "TODOISM_COMMAND"]),
    ("iterm2", ["iterm2", "-T", "todoism-dev", "zsh", "-c", "TODOISM_COMMAND"]),
]

def detect_current_terminal():
    """
    Attempt to detect the current terminal emulator by traversing the parent process tree.
    Returns the terminal name if detected, else None.
    """
    try:
        p = psutil.Process(os.getppid())
        while p:
            name = p.name().lower()
            for term, _ in TERMINALS:
                if term in name:
                    return term
            p = p.parent()
    except Exception as e:
        print(f"[WARN] Could not detect terminal emulator: {e}")
    return None

def find_terminal():
    # Try to detect the current terminal emulator first
    detected = detect_current_terminal()
    if detected:
        for name, cmd in TERMINALS:
            if name == detected and shutil.which(name):
                print(f"[INFO] Detected current terminal emulator: {name}")
                # Replace placeholder with actual command if present
                actual_cmd = [c if c != "TODOISM_COMMAND" else TODOISM_COMMAND for c in cmd]
                return (name, actual_cmd)
        print(f"[WARN] Detected terminal '{detected}' not found in system. Falling back.")
    # Fallback to first available terminal
    for name, cmd in TERMINALS:
        if shutil.which(name):
            actual_cmd = [c if c != "TODOISM_COMMAND" else TODOISM_COMMAND for c in cmd]
            return (name, actual_cmd)
    print("\033[91m[ERROR] No supported terminal emulator found.\033[0m")
    sys.exit(1)

def focus_window(window_title_substring="todoism-dev"):
    print(f"🎯 Focusing window containing title: {window_title_substring}")
    try:
        output = subprocess.check_output(["wmctrl", "-l"]).decode()
        for line in output.splitlines():
            if window_title_substring.lower() in line.lower():
                win_id = line.split()[0]
                subprocess.run(["wmctrl", "-ia", win_id])
                print("✅ Focused window.")
                return
        print("\033[91m[ERROR] Target window not found. Aborting test.\033[0m")
        sys.exit(1)
    except Exception as e:
        print(f"❌ wmctrl failed: {e}")
        sys.exit(1)

def launch_todoism():
    cmd = find_terminal()
    print(f"🚀 Launching: {' '.join(cmd[1])}")
    subprocess.Popen(cmd[1])

def keycode_needs_recording():
    """Check if keycodes need to be recorded"""
    try:
        settings_path = os.path.join("test", ".todoism", "settings.json")
        if not os.path.exists(settings_path):
            settings_path = os.path.expanduser("~/.todoism/settings.json")
        
        if not os.path.exists(settings_path):
            return True
            
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            # Check if any of the key codes are 0
            return (settings.get("ctrl+left", 0) == 0 or
                   settings.get("ctrl+right", 0) == 0 or
                   settings.get("ctrl+shift+left", 0) == 0 or
                   settings.get("ctrl+shift+right", 0) == 0 or
                   settings.get("alt+left", 0) == 0 or
                   settings.get("alt+right", 0) == 0)
    except Exception as _:
        return True

def record_keycodes():
    """Record the keycodes using the todoism command interface"""
    print("🎹 Recording keycodes using the :keycode record command...")
    
    # Wait for todoism to fully load
    time.sleep(TODOISM_LAUNCH_WAIT)
    focus_window()
    
    # Type command to record keycodes
    pyautogui.press(':')
    time.sleep(KEY_DELAY)
    
    command = "keycode record"
    for char in command:
        pyautogui.press(char)
        time.sleep(KEY_DELAY / 3)
    
    pyautogui.press('enter')
    time.sleep(ACTION_DELAY)
    
    # Handle the keycode recording process - press Enter to start
    pyautogui.press('enter')
    time.sleep(1)
    
    # Record each key combination
    key_combinations = [
        ['ctrl', 'left'],    # Ctrl+Left
        ['ctrl', 'right'],   # Ctrl+Right
        ['ctrl', 'shift', 'left'],  # Ctrl+Shift+Left
        ['ctrl', 'shift', 'right'], # Ctrl+Shift+Right
        ['alt', 'left'],     # Alt+Left
        ['alt', 'right']     # Alt+Right
    ]
    
    for combo in key_combinations:
        focus_window()
        print(f"🔑 Recording key combination: {'+'.join(combo)}")
        pyautogui.hotkey(*combo)
        time.sleep(1)
        
        # Press Enter to continue to next keycode
        focus_window()
        pyautogui.press('enter')
        time.sleep(1)
    
    # Wait for todoism to process the keycodes
    print("⏳ Waiting for keycode recording to complete...")
    time.sleep(3)

def emulate_keys():
    print(f"⏳ Waiting for todoism to load...")
    time.sleep(TODOISM_LAUNCH_WAIT)
    
    # First handle keycode recording if needed
    handle_keycode_recording()
    
    # Resume waiting to ensure the main todoism interface is loaded
    print(f"⏳ Waiting for main interface...")
    time.sleep(TODOISM_LAUNCH_WAIT)

    print("\n🤖 Sending keys with pyautogui...")

    focus_window()
    arrow_keys = ['down', 'up', 'down', 'down']
    for key in arrow_keys:
        focus_window()
        print(f"🔸 Pressing Arrow {key}")
        pyautogui.press(key)
        time.sleep(KEY_DELAY)

    time.sleep(ACTION_DELAY)

    # Test special key combinations
    focus_window()
    print("⌨️ Testing Ctrl+Left and Ctrl+Right navigation...")
    emulate_special_key('ctrl_left')
    time.sleep(KEY_DELAY)
    emulate_special_key('ctrl_right')
    time.sleep(KEY_DELAY)

    focus_window()
    print("📝 Pressing 'a' to add task...")
    pyautogui.press('a')
    time.sleep(ACTION_DELAY)

    print(f"🔤 Typing task char by char: {TASK_TEXT}")
    for char in TASK_TEXT:
        focus_window()
        print(f"   ↳ Typing '{char}'")
        pyautogui.press(char)
        time.sleep(KEY_DELAY / 3)

    focus_window()
    print("✅ Submitting task with Enter")
    pyautogui.press('enter')
    time.sleep(POST_TASK_VIEW_DELAY)

    focus_window()
    print("🚪 Pressing 'q' to quit")
    pyautogui.press('q')

    print("\n✅ All done!")

if __name__ == "__main__":
    print("\033[38;5;202m[INFO] The test window will be focused. Please do not interact with other windows, as real key inputs will be emulated!\033[0m")
    print("\033[38;5;202m[INFO] Press ENTER to confirm and start the test...\033[0m")
    while True:
        try:
            user_input = input()
            if user_input == '':
                break
            else:
                print("\033[38;5;202m[INFO] Please press only ENTER to start.\033[0m")
        except KeyboardInterrupt:
            print("\nAborted by user.")
            exit(1)
    launch_todoism()
    time.sleep(1)
    emulate_keys()
