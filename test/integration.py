import subprocess
import shutil
import sys
import time
import pyautogui

# --- Configuration ---
TODOISM_PATH = "/home/qichen/Dev/todoism"
TASK_TEXT = "Clean the kitchen"
TODOISM_COMMAND = f"cd {TODOISM_PATH} && python3 test/generate.py && python3 -m todoism --dev; exec zsh"
TODOISM_LAUNCH_WAIT = 2
KEY_DELAY = 0.3
ACTION_DELAY = 1.0
POST_TASK_VIEW_DELAY = 2.0

# --- Supported Terminals ---
TERMINALS = [
    ("gnome-terminal", ["gnome-terminal", "--title=todoism-dev", "--", "zsh", "-c", TODOISM_COMMAND]), # Updated title argument
    ("kitty", ["kitty", "-T", "todoism-dev", "zsh", "-c", TODOISM_COMMAND]), # Updated title
    ("alacritty", ["alacritty", "-t", "todoism-dev", "-e", "zsh", "-c", TODOISM_COMMAND]), # Updated title
    ("xterm", ["xterm", "-T", "todoism-dev", "-e", "zsh", "-c", TODOISM_COMMAND]), # Updated title
    ("konsole", ["konsole", "--new-tab", "-p", "tabtitle=todoism-dev", "-e", "zsh", "-c", TODOISM_COMMAND]), # Updated title
]

def focus_window(window_title_substring="todoism-dev"): # Updated default title
    print(f"🎯 Focusing window containing title: {window_title_substring}")
    try:
        output = subprocess.check_output(["wmctrl", "-l"]).decode()
        for line in output.splitlines():
            if window_title_substring.lower() in line.lower():
                win_id = line.split()[0]
                subprocess.run(["wmctrl", "-ia", win_id])
                print("✅ Focused window.")
                return
        print("⚠️  Target window not found.")
    except Exception as e:
        print(f"❌ wmctrl failed: {e}")

def find_terminal():
    for name, cmd in TERMINALS:
        if shutil.which(name):
            print(f"✅ Found terminal: {name}")
            return cmd
    print("❌ No supported terminal emulator found.")
    sys.exit(1)

def launch_todoism():
    cmd = find_terminal()
    print(f"🚀 Launching: {' '.join(cmd)}")
    subprocess.Popen(cmd)

def emulate_keys():
    print(f"⏳ Waiting {TODOISM_LAUNCH_WAIT} seconds for todoism to load...")
    time.sleep(TODOISM_LAUNCH_WAIT) # Keep initial wait for app load

    print("\n🤖 Sending keys with pyautogui...")

    focus_window() # Focus before first action
    arrow_keys = ['down', 'up', 'down', 'down']
    for key in arrow_keys:
        focus_window() # Focus before each arrow key press
        print(f"🔸 Pressing Arrow {key}")
        pyautogui.press(key)
        time.sleep(KEY_DELAY)

    time.sleep(ACTION_DELAY)

    focus_window() # Focus before pressing 'a'
    print("📝 Pressing 'a' to add task...")
    pyautogui.press('a')
    time.sleep(ACTION_DELAY)

    print(f"🔤 Typing task char by char: {TASK_TEXT}")
    for char in TASK_TEXT:
        focus_window() # Focus before each character
        print(f"   ↳ Typing '{char}'")
        pyautogui.press(char)
        time.sleep(KEY_DELAY / 3) # Add a small delay between chars

    focus_window() # Focus before pressing 'enter'
    print("✅ Submitting task with Enter")
    pyautogui.press('enter')
    time.sleep(POST_TASK_VIEW_DELAY)

    focus_window() # Focus before pressing 'q'
    print("🚪 Pressing 'q' to quit")
    pyautogui.press('q')

    print("\n✅ All done!")
    # pass

if __name__ == "__main__":
    launch_todoism()
    time.sleep(1) # Keep a short delay for window to appear initially
    emulate_keys()
