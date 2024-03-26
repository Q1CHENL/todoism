# todoism

An interactive and intuitive todo CLI

## ToDo

- **sidebar: categories**
- command autosort
- sound
- esc to quit exit() too slow
- command: done xx, goto xx
- command: date ymd, dmy
- invalid command
- custom theme
- set color random
- wrap a setup func for e.g paths
- update time regularly
- add mouse support
- command print overwriting
- can not fully display help when window too small
- ctl + shift to select multiple tasks to delete

## Install and use

- Install: `pip install todoism`
- Run: `todoism` or `todo`

```
┌──────────────────────────────────────────────────┐
│                                                  │
│   short commands:                                │
│   a - create new task                            │
│   d - mark task as done                          │
│   e - edit task                                  │
│   f - mark task as flagged                       │
│   q - quit this help message/todoism             │
│                                                  │
│   vim-like long commands:                        │            
│   (:<command> [args])                            │
│   :help - show this help message                 │
│   :purge - purge all done tasks                  │
│   :sort f - sort flagged tasks to top            │
│   :sort d - sort done tasks to bottom            │
│   :autosort f on|off                             │
│   :autosort d on|off                             │
│   :setcolor blue|red|yellow|green                │
│    - change background color of current task     │
│                                                  │
│   other key bindings:                            │
│   double Backspace - delete task                 │
│   ESC - quit adding/editing task                 │
│   Enter - finish adding/editing task             │
│   Up/Down Arrow Keys - navigate through tasks    │
│                                                  │
└──────────────────────────────────────────────────┘
```
