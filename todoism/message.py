# This file contains all message templates for the application

help_msg = '''
┌──────────────────────────────────────────────────┐
│                                                  │
│   Short commands:                                │
│   a - Create new task/category                   │
│   d - Mark task as done                          │
│   e - Edit task/category                         │
│   f - Mark task as flagged                       │
│   q - Quit this help message/todoism             │
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
│   :del [task_id] - Delete task                   │
│   :edit [task_id] - Edit task                    │
│   :done [task_id] - Mark task as done            |
│   :purge - Purge all done tasks                  │
│   :sort f - Sort flagged tasks to top            │
│   :sort d - Sort done tasks to bottom            │
│   :autosort f on|off                             │
│   :autosort d on|off                             │
│   :color blue|red|yellow|green                   │
│    - Change background color of current task     │
│   :st on|off - toggle strikethrough effect       │
│                                                  │
└──────────────────────────────────────────────────┘
'''

empty_msg = '''
┌──────────────────────────────────────────────────────┐
│       Hmm, it seems there are no active tasks        │
│     Take a break, or create some to get busy :)      │
└──────────────────────────────────────────────────────┘
'''

limit_msg = '''
┌────────────────────────────────────────┐
│   You already have 99 tasks in hand.   │
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
│                                                           │
│ This takes just a few seconds and saves your settings!    │
│                                                           │
│ Press Enter key to start...                               │
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

# Replace formatting placeholders with static text
keycode_feedback_ctrl_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Left                             │
│                                                   │
│ Press Enter to continue...                        │
└───────────────────────────────────────────────────┘
'''

keycode_feedback_ctrl_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Right                            │
│                                                   │
│ Press Enter to continue...                        │
└───────────────────────────────────────────────────┘
'''

keycode_feedback_ctrl_shift_left_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Shift + Left                     │
│                                                   │
│ Press Enter to continue...                        │
└───────────────────────────────────────────────────┘
'''

keycode_feedback_ctrl_shift_right_msg = '''
┌───────────────────────────────────────────────────┐
│ Recorded: Ctrl + Shift + Right                    │
│                                                   │
│ Press Enter to continue...                        │
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
│                                                   │
└───────────────────────────────────────────────────┘
'''