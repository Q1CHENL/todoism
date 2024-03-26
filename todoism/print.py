import curses
from datetime import datetime


add_mode  = 0
edit_mode = 1

help_msg =  '''
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
            '''

def print_help(stdscr):
    height, width = stdscr.getmaxyx()
    stdscr.addstr(0, 0, help_msg)
    stdscr.refresh()
    # (width // 2) + 50
    # (height // 2) - 4

# The core function to print task
def print_task(stdscr, task, y):
    max_y = stdscr.getmaxyx()[0] 
    # handle task overflow
    if y < max_y:
        stdscr.addstr(y, 0, f"{'✅' if task['status'] else '  '} {' ' if task['id'] < 10 else ''}{task['id']}. {task['description'] + (75 - len(task['description'])) * ' ' + task['date']} {'🚩' if task['flagged'] else ''}" )

def print_task_highlighted(stdscr, task, y):
    stdscr.attron(curses.color_pair(1))
    print_task(stdscr, task, y)
    stdscr.attroff(curses.color_pair(1))        

def print_task_mode(stdscr, task, y, mode):
    if mode == edit_mode:
        print_task_highlighted(stdscr, task, y)
    else:
        print_task(stdscr, task, y)  
        
def print_tasks(stdscr, tasks, current_id, start, end):
    if start > 0:
        for i, task in enumerate(tasks[start - 1:end + 1]):
            if i + start == current_id: # handle task overflow: +start
                print_task_highlighted(stdscr, task, i + 1) # +1 due to status bar
            else:
                print_task(stdscr, task, i + 1)

def print_status_bar(stdscr, done_cnt, task_cnt):
    percentage_num = int((done_cnt / task_cnt) * 100) if task_cnt > 0 else 0
    status_bar = {
        'tasks': f'{' '*35}Progress: {done_cnt}/{task_cnt} {percentage_num if task_cnt > 0 else 0}%',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M") 
    }
    
    color_pair = 0
    if percentage_num >= 67:
        color_pair = 2
    elif percentage_num >= 33:
        color_pair = 3
    else:
        if task_cnt == 0:
            color_pair = 5
        else:
            color_pair = 4
            
    stdscr.attron(curses.color_pair(color_pair))    
    stdscr.addstr(0, 0, f"{status_bar['tasks']}")
    stdscr.attroff(curses.color_pair(color_pair))
    stdscr.addstr(f" | {status_bar['date']}")
    stdscr.refresh()
