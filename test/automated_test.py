import subprocess
import shutil
import sys
import time
import pyautogui

# --- Configuration ---
TODOISM_PATH = "/home/qichen/Dev/todoism"
TASK_TEXT = "Clean the kitchen"
TODOISM_COMMAND = f"cd {TODOISM_PATH} && python3 -m todoism --dev; exec zsh"
TODOISM_LAUNCH_WAIT = 3.5
KEY_DELAY = 0.3
ACTION_DELAY = 1.0
POST_TASK_VIEW_DELAY = 2.0

# --- Supported Terminals ---
TERMINALS = [
    ("gnome-terminal", ["gnome-terminal", "--", "zsh", "-c", TODOISM_COMMAND]),
    ("kitty", ["kitty", "-T", "todoism-run", "zsh", "-c", TODOISM_COMMAND]),
    ("alacritty", ["alacritty", "-t", "todoism-run", "-e", "zsh", "-c", TODOISM_COMMAND]),
    ("xterm", ["xterm", "-T", "todoism-run", "-e", "zsh", "-c", TODOISM_COMMAND]),
    ("konsole", ["konsole", "--new-tab", "-p", "tabtitle=todoism-run", "-e", "zsh", "-c", TODOISM_COMMAND]),
]

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
    time.sleep(TODOISM_LAUNCH_WAIT)

    print("\n🤖 Sending keys with pyautogui...")

    arrow_keys = ['down', 'up', 'down', 'down']
    for key in arrow_keys:
        print(f"🔸 Pressing Arrow {key}")
        pyautogui.press(key)
        time.sleep(KEY_DELAY)

    time.sleep(ACTION_DELAY)

    print("📝 Pressing 'a' to add task...")
    pyautogui.press('a')
    time.sleep(ACTION_DELAY)

    print(f"🔤 Typing task: {TASK_TEXT}")
    pyautogui.typewrite(TASK_TEXT, interval=KEY_DELAY / 2)

    print("✅ Submitting task with Enter")
    pyautogui.press('enter')
    time.sleep(POST_TASK_VIEW_DELAY)

    print("🚪 Pressing 'q' to quit")
    pyautogui.press('q')

    print("\n✅ All done!")

if __name__ == "__main__":
    launch_todoism()
    emulate_keys()
