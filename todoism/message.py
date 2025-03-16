# This file contains all message templates for the application

help_msg = '''
┌──────────────────────────────────────────────────┐
│                                                  │
│   Short commands:                                │
│   a - Create new task/category                   │
│   d - Mark task as done                          │
│   e - Edit task/category                         │
│   f - Mark task as flagged                       │
│   q - Quit this help message/pref panel/todoism  │
│                                                  │
│   Key bindings:                                  │
│   Tab - Toggle focus bewteen tasks and sidebar   │
│   Double Backspace - delete task                 │
│   ESC - quit adding/editing task                 │
│   Enter - finish adding/editing task             │
│   Up/Down Arrow Keys - navigate through tasks    │
│   Mouse Click:                                   │
│    - on task: Select task                        │
│    - on category: Select category                │
│    - on done: Toggle task completion             │
│    - on flag: Toggle task flag                   │
│    - on blank area: toggle focus                 │
│                                                  │
│   Vim-like long commands:                        │
│   (:<command> [args])                            │
│   :help - Show this help message                 │
│   :pref - Open preference panel                  │
│   :del <task_id> - Delete task                   │
│   :edit <task_id> - Edit task                    │
│   :done <task_id> - Mark task as done            |
│   :purge - Purge all done tasks                  │
│                                                  │
└──────────────────────────────────────────────────┘
'''

pref_panel = '''
┌────────────────────────────────────┐
│                                    │
│   Tag: on|off                      │
│                                    │
│   Strikethrough: on|off            │
│                                    │
│   Color: blue|red|yellow|green     │
│                                    │
│   Date format: Y-M-D|D-M-Y|M-D-Y   │
│                                    │
│   Sort by flagged: on|off          │
│                                    │
│   Sort by done: on|off             │
│                                    │
│   (Press Tab to toggle options)    │
│                                    │
└────────────────────────────────────┘

'''

empty_msg = '''
┌──────────────────────────────────────────────────────┐
│       Hmm, it seems there are no active tasks        │
│     Take a break, or create some to get busy :)      │
└──────────────────────────────────────────────────────┘
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
│ Keycode Recording (1/4)                           │
│                                                   │
│ Press Ctrl + Left key combination                 │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_recording_ctrl_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (2/4)                           │
│                                                   │
│ Press Ctrl + Right key combination                │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_recording_ctrl_shift_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (3/4)                           │
│                                                   │
│ Press Ctrl + Shift + Left key combination         │
│                                                   │
│ Press 'r' to restart the recording process        │
│ Press 'q' to quit (your settings won't be saved)  │
└───────────────────────────────────────────────────┘
'''

keycode_recording_ctrl_shift_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Keycode Recording (4/4)                           │
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