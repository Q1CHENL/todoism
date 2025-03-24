# This file contains all message templates for the application

help_msg = '''
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                             │
│                                       todoism v1.21.5                                       │
│                                                                                             │
│                               Visit Github page for more info                               │
│                                                                                             │
│                                                                                             │
│   Short commands:                            Key bindings:                                  │
│   a - Create new task/category               Tab - Toggle focus bewteen tasks and sidebar   │
│   d - Mark task as done                      Double Backspace - delete task/category        │
│   e - Edit task/category                     ESC - Cancel adding/editing/search             │
│   f - Mark task as flagged                   Enter - Finish adding/editing, confirm search  │
│   q - Quit this help/pref/search/todoism     Up/Down Arrow Keys - Navigate through tasks    │
│                                              CTRL + Left/Right - Move by word               │
│   Vim-like long commands:                    CTRL + Shift + Left/Right - Select by word     │
│   :help - Show this help message             ALT + Left/Right - Jump to start/end of text   │
│   :pref - Open preference panel                                                             │
│   :del <task_id> - Delete task               Mouse Operations:                              │
│   :edit <task_id> - Edit task                - Click on task/category: Select item          │
│   :done <task_id> - Mark task as done        - Click on done/flag: Toggle status            │
│   :purge - Purge done tasks in current cat.  - Click on blank area: Toggle focus            │
│   :purge all - Purge all done tasks          - Wheel scroll: Navigate through tasks/cats    │
│                                                                                             │
│   To add due date to a task:                 To search for tasks:                           │
│   Add [<due date>] at the end of the task    /<search term>                                 │
│   Supported formats:                                                                        │
│   - [yyyy-mm-dd hh:mm]    - [hh:mm]                                                         │
│   - [yyyy-mm-dd]          - [mm-dd hh:mm]                                                   │
│   - [mm-dd] or [dd-mm]                                                                      │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
'''

pref_panel = '''
┌───────────────────────────────────────┐
│                                       │
│   Tag: on|off                         │
│                                       │
│   Strikethrough: on|off               │
│                                       │
│   Color: purple|cyan|blue|red|yellow  │
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

no_tasks_found_msg = '''
┌────────────────────────────┐
│      No tasks found :)     │
└────────────────────────────┘
'''

empty_msg = '''
┌──────────────────────────────────┐
│      No active tasks here :)     │
└──────────────────────────────────┘
'''

limit_msg = '''
┌────────────────────────────────────────┐
│  You already have 1024 tasks in hand.  │
│  Maybe try to deal with them first :)  │
└────────────────────────────────────────┘
'''

keycode_msg = '''
┌───────────────────────────────────────────────────────────┐
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

# Key recording message templates - fixed indentation and formatting
keycode_recording_ctrl_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (1/6)                           │
│                                                   │
│ Press Ctrl + Left key combination                 │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_recording_ctrl_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (2/6)                           │
│                                                   │
│ Press Ctrl + Right key combination                │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_recording_ctrl_shift_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (3/6)                           │
│                                                   │
│ Press Ctrl + Shift + Left key combination         │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_recording_ctrl_shift_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (4/6)                           │
│                                                   │
│ Press Ctrl + Shift + Right key combination        │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_recording_alt_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (5/6)                           │
│                                                   │
│ Press Alt + Left key combination                  │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_recording_alt_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (6/6)                           │
│                                                   │
│ Press Alt + Right key combination                 │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

# Replace formatting placeholders with static text
keycode_feedback_ctrl_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Left                             │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_feedback_ctrl_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Right                            │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_feedback_ctrl_shift_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Shift + Left                     │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_feedback_ctrl_shift_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Shift + Right                    │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_feedback_alt_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Alt + Left                              │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_feedback_alt_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Alt + Right                             │
│                                                   │
│ Press Enter to continue                           │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_completion_msg = '''
┌───────────────────────────────────────────────────┐
│ Key codes successfully saved!                     │
│                                                   │
│ Todoism will now start...                         │
└───────────────────────────────────────────────────┘
'''

keycode_restart_msg = '''
┌───────────────────────────────────────────────────┐
│ Restarting key recording...                       │
└───────────────────────────────────────────────────┘
'''
