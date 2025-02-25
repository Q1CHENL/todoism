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

def print_task(stdscr, task, row, is_current, max_x):
    """Print a task with status indicators"""
    if max_x == 0:  # Get max_x if not provided
        max_x = stdscr.getmaxyx()[1]
        
    stdscr.move(row, 0)
    stdscr.clrtoeol()  # Clear only this line
    
    # Print task ID
    stdscr.addstr(row, 0, f"{task['id']:2d} ")
    
    # Print status indicator with color
    if task.get('status', False):
        stdscr.attron(curses.color_pair(6))    
        stdscr.addstr(row, 3, "✓")
        stdscr.attroff(curses.color_pair(6))
    else:
        stdscr.addstr(row, 3, " ")
    
    # Print flag indicator with color
    if task.get('flagged', False):
        stdscr.attron(curses.color_pair(7))    
        stdscr.addstr(row, 5, "⚑")
        stdscr.attroff(curses.color_pair(7))
    else:
        stdscr.addstr(row, 5, " ")
    
    # Calculate remaining space for description and date
    date_str = task['date']
    base_length = 7  # Length of ID + status + flag area
    date_padding = 2  # Space between description and date
    
    # Calculate maximum description length
    max_desc_space = max_x - base_length - len(date_str) - date_padding
    
    # Handle description truncation
    if len(task['description']) > max_desc_space - 3:
        description = task['description'][:max_desc_space-3] + "..."
    else:
        description = task['description']
    
    # Calculate padding for date alignment
    padding_length = max_x - base_length - len(description) - len(date_str) - 1
    padding = " " * max(1, padding_length)
    
    # Print description and date with proper highlighting if current
    if is_current:
        stdscr.attron(curses.A_REVERSE)
    stdscr.addstr(row, 7, f"{description}{padding}{date_str}")
    if is_current:
        stdscr.attroff(curses.A_REVERSE)

def print_task_selected(stdscr, task, y):
    stdscr.attron(curses.color_pair(1))
    print_task(stdscr, task, y, False, 0)
    stdscr.attroff(curses.color_pair(1))        

def print_task_mode(stdscr, task, y, mode):
    """mode: add/edit"""
    if mode == edit_mode:
        print_task_selected(stdscr, task, y)
    else:
        print_task(stdscr, task, y, False, 0)  
        
def print_tasks(stdscr, task_list, current_id, start, end):
    if start > 0:
        for i, task in enumerate(task_list[start - 1:end]):
            if i + start == current_id: # handle task overflow: +start
                print_task_selected(stdscr, task, i + 1) # +1 due to status bar
                stdscr.refresh()
            else:
                print_task(stdscr, task, i + 1, task['id'] == current_id, 0)
                stdscr.refresh()


def print_status_bar(stdscr, done_cnt, task_cnt):
    """Print centered status bar with progress, percentage, date and time"""
    max_y, max_x = stdscr.getmaxyx()
    percentage = f"({(done_cnt/task_cnt)*100:.0f}%)" if task_cnt > 0 else "(0%)"
    status = f"Done: {done_cnt}/{task_cnt} {percentage}"
    
    # Format current date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime("%Y-%m-%d")
    time_str = current_datetime.strftime("%H:%M")
    datetime_str = f"{date_str} {time_str}"
    
    # Calculate center position
    total_len = len(status) + len(datetime_str) + 2  # +2 for spacing
    start_pos = (max_x - total_len) // 2
    
    # Clear only the top line
    stdscr.move(0, 0)
    stdscr.clrtoeol()
    
    # Print centered status and datetime
    stdscr.addstr(0, start_pos, status)
    stdscr.addstr(0, start_pos + len(status) + 2, datetime_str)

def print_main_view(stdscr, done_cnt, task_cnt, tasks, current_id, start, end):
    print_status_bar(stdscr, done_cnt, task_cnt)
    print_tasks(stdscr, tasks, current_id, start, end)
    
def repaint(stdscr, done_cnt, task_cnt, task_list, current_id, start, end):
    """Update screen efficiently without full clear"""
    max_y, max_x = stdscr.getmaxyx()
    
    # Update status bar
    print_status_bar(stdscr, done_cnt, task_cnt)
    
    # Update tasks
    for i in range(start-1, end):
        if i < len(task_list):
            task = task_list[i]
            print_task(stdscr, task, i - (start-1) + 1, task['id'] == current_id, max_x)
    
    # Clear any remaining lines if tasks were deleted
    for i in range(end - start + 2, max_y):
        stdscr.move(i, 0)
        stdscr.clrtoeol()
    
    # Single screen update
    stdscr.noutrefresh()
    curses.doupdate()

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

def print_task_symbols(stdscr, task, y, x):
    """Print task symbols (done and flag) with appropriate colors"""
    if task['status']:
        stdscr.attron(curses.color_pair(6))  # Green
        stdscr.addstr(y, x, "✓")
        stdscr.attroff(curses.color_pair(6))
    else:
        stdscr.addstr(y, x, " ")
    
    if task['flagged']:
        stdscr.attron(curses.color_pair(7))  # Orange/Yellow
        stdscr.addstr(y, x + 1, "⚑")
        stdscr.attroff(curses.color_pair(7))
    else:
        stdscr.addstr(y, x + 1, " ")
