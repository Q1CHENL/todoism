# This file contains all message templates for the application

HELP_MSG = '''
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                              │
│                  ████████╗ ██████╗ ██████╗  ██████╗ ██╗███████╗███╗   ███╗                   │
│                  ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗██║██╔════╝████╗ ████║                   │
│                     ██║   ██║   ██║██║  ██║██║   ██║██║███████╗██╔████╔██║                   │
│                     ██║   ██║   ██║██║  ██║██║   ██║██║╚════██║██║╚██╔╝██║                   │
│                     ██║   ╚██████╔╝██████╔╝╚██████╔╝██║███████║██║ ╚═╝ ██║                   │
│                     ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═╝     ╚═╝                   │
│                                                                                              │
│                               Visit Github page for more info                                │
│                                                                                              │
│                                                                                              │
│   Short commands:                            Key bindings:                                   │
│   a - Create new task/category               Tab - Toggle focus bewteen tasks and sidebar    │
│   d - Mark task as done                      Double Backspace - delete task/category         │
│   e - Edit task/category                     ESC - Cancel adding/editing/search              │
│   f - Mark task as flagged                   Enter - Finish adding/editing, confirm search   │
│   q - Quit this help/pref/search/todoism     Up/Down Arrow Keys - Navigate through tasks     │
│                                              CTRL + Left/Right - Move by word                │
│   Vim-like long commands:                    CTRL + Shift + Left/Right - Select by word      │
│   :help - Show this help message             ALT + Left/Right                                │
│   :pref - Open preference panel                  - Jump to start/end of text                 │
│   :del <task_id> - Delete task                   - Jump to top/bottom                        │
│   :edit <task_id> - Edit task                                                                │
│   :done <task_id> - Mark task as done        Mouse Operations:                               │
│   :purge - Purge done tasks in current cat.  - Click on task/category: Select item           │
│   :purge all - Purge all done tasks          - Click on done/flag: Toggle status             │
│   :keycode record - record keycodes          - Click on blank area: Toggle focus             │
│   :keycode show - show keycodes              - Wheel scroll: Navigate through tasks/cats     │
│                                                                                              │
│   To add due date to a task:                 To search for tasks:                            │
│   Add [<due date>] at the end of the task    /<search term>                                  │
│   Supported formats:                                                                         │
│   - [yyyy-mm-dd hh:mm]    - [hh:mm]                                                          │
│   - [yyyy-mm-dd]          - [mm-dd hh:mm]                                                    │
│   - [mm-dd] or [dd-mm]                                                                       │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
'''

PREF_PANEL = '''
┌───────────────────────────────────────┐
│                                       │
│   Strikethrough: on|off               │
│                                       │
│   Bold Text: on|off                   │
│                                       │
│   Tag in All Tasks: on|off            │
│                                       │
│   Theme: purple|cyan|blue|red|yellow  │
│                                       │
│   Date format: Y-M-D|D-M-Y|M-D-Y      │
│                                       │
│   Sort by flagged: on|off             │
│                                       │
│   Sort by done: on|off                │
│                                       │
│   (Press Tab to toggle options)       │
│                                       │
└───────────────────────────────────────┘

'''

NO_TASKS_FOUND_MSG = '''
┌────────────────────────────┐
│      No tasks found :)     │
└────────────────────────────┘
'''

EMPTY_MSG = '''
┌──────────────────────────────────┐
│      No active tasks here :)     │
└──────────────────────────────────┘
'''

LIMIT_MSG = '''
┌────────────────────────────────────────┐
│  You already have 1024 tasks in hand.  │
│  Maybe try to deal with them first :)  │
└────────────────────────────────────────┘
'''

KEYCODE_MSG = '''
┌───────────────────────────────────────────────────────────┐
│                                                           │
│ ████████╗ ██████╗ ██████╗  ██████╗ ██╗███████╗███╗   ███╗ │
│ ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗██║██╔════╝████╗ ████║ │
│    ██║   ██║   ██║██║  ██║██║   ██║██║███████╗██╔████╔██║ │
│    ██║   ██║   ██║██║  ██║██║   ██║██║╚════██║██║╚██╔╝██║ │
│    ██║   ╚██████╔╝██████╔╝╚██████╔╝██║███████║██║ ╚═╝ ██║ │
│    ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═╝     ╚═╝ │
│                                                           │
│ Welcome!                                                  │
│ Let's set up keycodes for todoism to work properly!       │
│                                                           │
│ Press these keys when prompted:                           │
│ - Ctrl + Left                                             │
│ - Ctrl + Right                                            │
│ - Ctrl + Shift + Left                                     │
│ - Ctrl + Shift + Right                                    │
│ - Alt + Left                                              │
│ - Alt + Right                                             │
│                                                           │
│ This takes just a few seconds!                            │
│                                                           │
│ Press Enter to start                                      │
│ Press 'q' to quit (your settings won't be saved)          │
└───────────────────────────────────────────────────────────┘
'''

KEYCODE_RECORDING_CTRL_LEFT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (1/6)                           │
│                                                   │
│ Press Ctrl + Left key combination                 │
│                                                   │
│ Press Enter to skip                               │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_RECORDING_CTRL_RIGHT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (2/6)                           │
│                                                   │
│ Press Ctrl + Right key combination                │
│                                                   │
│ Press Enter to skip                               │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_RECORDING_CTRL_SHIFT_LEFT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (3/6)                           │
│                                                   │
│ Press Ctrl + Shift + Left key combination         │
│                                                   │
│ Press Enter to skip                               │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_RECORDING_CTRL_SHIFT_RIGHT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (4/6)                           │
│                                                   │
│ Press Ctrl + Shift + Right key combination        │
│                                                   │
│ Press Enter to skip                               │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_RECORDING_ALT_LEFT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (5/6)                           │
│                                                   │
│ Press Alt + Left key combination                  │
│                                                   │
│ Press Enter to skip                               │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_RECORDING_ALT_RIGHT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (6/6)                           │
│                                                   │
│ Press Alt + Right key combination                 │
│                                                   │
│ Press Enter to skip                               │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_CTRL_LEFT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Left                             │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_CTRL_RIGHT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Right                            │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_CTRL_SHIFT_LEFT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Shift + Left                     │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_CTRL_SHIFT_RIGHT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Shift + Right                    │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_ALT_LEFT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Alt + Left                              │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_ALT_RIGHT_MSG = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Alt + Right                             │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_CTRL_LEFT_MSG_SKIPPED = '''
┌───────────────────────────────────────────────────┐
│ Skipped: Ctrl + Left                              │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_CTRL_RIGHT_MSG_SKIPPED = '''
┌───────────────────────────────────────────────────┐
│ Skipped: Ctrl + Right                             │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_CTRL_SHIFT_LEFT_MSG_SKIPPED = '''
┌───────────────────────────────────────────────────┐
│ Skipped: Ctrl + Shift + Left                      │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_CTRL_SHIFT_RIGHT_MSG_SKIPPED = '''
┌───────────────────────────────────────────────────┐
│ Skipped: Ctrl + Shift + Right                     │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_ALT_LEFT_MSG_SKIPPED = '''
┌───────────────────────────────────────────────────┐
│ Skipped: Alt + Left                               │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_FEEDBACK_ALT_RIGHT_MSG_SKIPPED = '''
┌───────────────────────────────────────────────────┐
│ Skipped: Alt + Right                              │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

KEYCODE_COMPLETION_MSG = '''
┌───────────────────────────────────────────────────┐
│ Key codes successfully saved!                     │
│                                                   │
│ Todoism will now start...                         │
└───────────────────────────────────────────────────┘
'''

KEYCODE_RESTART_MSG = '''
┌───────────────────────────────────────────────────┐
│ Restarting key recording...                       │
└───────────────────────────────────────────────────┘
'''

NEW_VERSION_MSG = '''
┌───────────────────────────────────────────────────┐
│ New version of todoism is available!              │
│                                                   │
│ Press 'u' to update now                           │
│ Press Enter to proceed without updating           │
└───────────────────────────────────────────────────┘
'''

UPDATE_SUCCESS_MSG = '''
┌───────────────────────────────────────────────────────────┐
│ ████████╗ ██████╗ ██████╗  ██████╗ ██╗███████╗███╗   ███╗ │
│ ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗██║██╔════╝████╗ ████║ │
│    ██║   ██║   ██║██║  ██║██║   ██║██║███████╗██╔████╔██║ │
│    ██║   ██║   ██║██║  ██║██║   ██║██║╚════██║██║╚██╔╝██║ │
│    ██║   ╚██████╔╝██████╔╝╚██████╔╝██║███████║██║ ╚═╝ ██║ │
│    ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═╝     ╚═╝ │
│                                                           │
│          Sucessfully updated to todoism v1.21.8!          │
│                                                           │
│          What's new:                                      │
│          - Bold text support                              │
│          - Various Bug fixes and improvements             │
│                                                           │
│          Please press 'q' to exit and restart.            │
└───────────────────────────────────────────────────────────┘
'''

UPDATE_FAILURE_MSG = '''
┌─────────────────────────────────────────────────────┐
│   Failed to update todoism. Some error occurred.    │
│                                                     │
│   Check your internet connection and try again.     │
│   Or run 'pip install todoism --upgrade'            │
│   to update manually.                               │
│                                                     │
│   Will proceed with current version...              │
└─────────────────────────────────────────────────────┘
'''

def keycode_summary():
    """Constructs a message for the given keycode"""
    import todoism.keycode as kc
    msg =  f"""
    ┌───────────────────────────────────────────────┐
    │   CTRL + LEFT: {kc.CTRL_LEFT}                            │
    │                                               │
    │   CTRL + RIGHT: {kc.CTRL_RIGHT}                           │
    │                                               │
    │   CTRL + SHIFT + LEFT: {kc.CTRL_SHIFT_LEFT}                    │
    │                                               │
    │   CTRL + SHIFT + RIGHT: {kc.CTRL_SHIFT_RIGHT}                   │
    │                                               │
    │   ALT + LEFT: {kc.ALT_LEFT}                             │
    │                                               │
    │   ALT + RIGHT: {kc.ALT_RIGHT}                            │
    └───────────────────────────────────────────────┘
    """
    return msg
