# todoism

An interactive and intuitive todo CLI

## ToDo

1. command autosort
2. sound
3. esc to quit exit() too slow
4. save settings
5. deleting all tasks from top in current window leads to weird view
6. edit to empty == delete -> implement a delete for both edit-delete and 2x backspace
7. <ref=<https://www.reddit.com/r/learnpython/comments/162kjgj/a_satisfying_solution_to_avoid_circular>
8. command: done xx, goto xx
9. command: date ymd, dmy
10. color pairs
11. sidebar: categories!!!
12. invalid command
13. custom theme
14. set color random
15. wrap a setup func for e.g paths

## Install and use

`pip install todoism`

```py
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
