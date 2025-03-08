# todoism

A simple and easy-to-use todo TUI

## Screenshot

![UI](./assets/screenshot-v1.21.2.png)

## Install and use

- Install: `pip install todoism`
- Run: `todoism` or `todo`
- Update: `pip install todoism --upgrade`

```txt
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
│   :setcolor blue|red|yellow|green                │
│    - Change background color of current task     │
│   :st on|off - toggle strikethrough effect       │
│                                                  │
└──────────────────────────────────────────────────┘
```

> [!NOTE]
> Some terminal does not support mouse click or strike through effect.

## ToDos

- properly display completed tasks
- maybe make autosort flag and done default
- grey background when adding new task using 'a'
- make status bar prettier: wrap it as a block
- add multi language support
- make no-task message more helpful
- command autosort
- emulate the popup menu when right click on task
- esc to quit exit() too slow
- command: date ymd, dmy
- custom theme
- wrap a setup func for e.g paths
- ctl + shift to select multiple tasks to delete/done
- group different kinds of tasks
- simplify print args
- history total done count in maybe settings
- sound

## Contribute

Issues and PRs are welcome! todoism uses curses library as its main tech stack. Please refer to the library [docs](https://docs.python.org/3/library/curses.html#module-curses) and [how-to](https://docs.python.org/3/howto/curses.html) to get started.
