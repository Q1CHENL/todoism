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
│   :del [task_id] - delete task                   │
│   :edit [task_id] - edit task                    │
│   :done [task_id] - mark task as done            │
│                                                  │
│   other key bindings:                            │
│   double Backspace - delete task                 │
│   ESC - quit adding/editing task                 │
│   Enter - finish adding/editing task             │
│   Up/Down Arrow Keys - navigate through tasks    │
│                                                  │
└──────────────────────────────────────────────────┘
'''

empty_msg = f'''
┌──────────────────────────────────────────────────────┐
│       Hmm, it seems there are no active tasks        │
│ Take a break, or create some new ones to get busy :) │
└──────────────────────────────────────────────────────┘
'''

limit_msg = f'''
┌────────────────────────────────────────┐
│   You already have 99 tasks in hand.   │
│  Maybe try to deal with them first :)  │
└────────────────────────────────────────┘
'''

def print_msg(stdscr, msg):
    lines = msg.split('\n')
    width = len(lines[1])
    max_x = stdscr.getmaxyx()[1]
    final_str = '\n'.join([' ' * ((max_x - width) // 2) + line for line in lines])
    stdscr.addstr(1, 0, f"{final_str}")
    stdscr.refresh()

def print_version():
    print("todoism version 1.20")

# The core function to print a single task
def print_task(stdscr, task, y):
    max_y, max_x= stdscr.getmaxyx()
    # 16: date length, 7: front indent, 3: flag
    spaces = (max_x - 1 - 7 - 16 - len(task['description']) - 3) * ' '
    description_with_spaces = task['description'] + spaces
    status = '✅' if task['status'] else '  '
    flag = '🚩' if task['flagged'] else ''
    id_str = (' ' if task['id'] < 10 else '') + str(task['id'])
    if y < max_y:
        stdscr.addstr(y, 0, f"{status} {id_str}. {description_with_spaces + task['date']} {flag}")
        
def print_task_selected(stdscr, task, y):
    stdscr.attron(curses.color_pair(1))
    print_task(stdscr, task, y)
    stdscr.attroff(curses.color_pair(1))        

def print_task_mode(stdscr, task, y, mode):
    """mode: add/edit"""
    if mode == edit_mode:
        print_task_selected(stdscr, task, y)
    else:
        print_task(stdscr, task, y)  
        
def print_tasks(stdscr, task_list, current_id, start, end):
    if start > 0:
        for i, task in enumerate(task_list[start - 1:end]):
            if i + start == current_id: # handle task overflow: +start
                print_task_selected(stdscr, task, i + 1) # +1 due to status bar
                stdscr.refresh()
            else:
                print_task(stdscr, task, i + 1)
                stdscr.refresh()


def print_status_bar(stdscr, done_cnt, task_cnt):
    """Example: Progress: 16/69 23% | 2024-03-27 01:53"""
    
    max_x= stdscr.getmaxyx()[1]
    side_spaces = ((max_x - 38) // 2) * ' '
    percentage_num = int((done_cnt / task_cnt) * 100) if task_cnt > 0 else 0
    status_bar = {
        'tasks': f"Progress: {done_cnt}/{task_cnt} {percentage_num if task_cnt > 0 else 0}%",
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
    stdscr.addstr(0, 0, f"{side_spaces}{status_bar['tasks']}")
    stdscr.attroff(curses.color_pair(color_pair))
    stdscr.addstr(f" | {status_bar['date']}{side_spaces}")
    stdscr.refresh()

def print_main_view(stdscr, done_cnt, task_cnt, tasks, current_id, start, end):
    print_status_bar(stdscr, done_cnt, task_cnt)
    print_tasks(stdscr, tasks, current_id, start, end)
    
def repaint(stdscr, done_cnt, task_cnt, task_list, current_id, start, end):
    """Clear the current view and repaint everything"""
    stdscr.clear()
    print_main_view(stdscr, done_cnt, task_cnt, task_list, current_id, start, end)
    stdscr.refresh()

def print_category(sidebar_win, category, y):
    max_y, max_x= sidebar_win.getmaxyx()
    if y < max_y:
        sidebar_win.addstr(y, 0, f"{category['name']}")
    
def print_category_selected(siderbar_win, category, y):
    siderbar_win.attron(curses.color_pair(1))
    print_category(siderbar_win, category, y)
    siderbar_win.attroff(curses.color_pair(1))        
        
def print_siderbar(sidebar_win, categories, current_category_id, start, end):
    if start > 0:
        for i, task in enumerate(categories[start - 1:end]):
            if i + start == current_category_id: # handle task overflow: +start
                print_category_selected(sidebar_win, task, i + 1) # +1 due to status bar
                sidebar_win.refresh()
            else:
                print_category(sidebar_win, task, i + 1)
                sidebar_win.refresh()
        

def print_all_cli(todos):
    if len(todos) == 0:
        print("no todos yet")
        exit(0)
    flagged_fmt = "\033[3m%s\033[0m" # italic
    done_fmt = "\033[9m%s\033[0m" # crossline
    todo_fmt = "#{id:02d} {description} ({date})"
    text = ""
    for todo in todos:
        todo_line = todo_fmt.format(**todo)
        if todo.get("status"):
            todo_line = done_fmt % todo_line
        if todo.get("flagged"):
            todo_line = flagged_fmt % todo_line
        text += todo_line + "\n"
    print(text, end="")
