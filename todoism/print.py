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
│   :del [task_id] - delete task                   │
│   :edit [task_id] - edit task                    │
│   :done [task_id] - mark task as done            |
│   :purge - purge all done tasks                  │
│   :sort f - sort flagged tasks to top            │
│   :sort d - sort done tasks to bottom            │
│   :autosort f on|off                             │
│   :autosort d on|off                             │
│   :setcolor blue|red|yellow|green                │
│    - change background color of current task     │
│   :st on|off - toggle strikethrough effect       │ 
│                                                  │
│   other key bindings:                            │
│   double Backspace - delete task                 │
│   ESC - quit adding/editing task                 │
│   Enter - finish adding/editing task             │
│   Up/Down Arrow Keys - navigate through tasks    │
│    Mouse Click:                                  │
│    - on task: select task                        │
│    - on done: toggle task completion             │
│    - on flag: toggle task flag                   │  
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

def print_task_symbols(stdscr, task, y, status_x=3, flag_x=5, use_colors=True, is_selected=False):
    """Print task status and flag symbols with appropriate colors
    
    Args:
        stdscr: The curses window
        task: The task data dictionary
        y: The row position
        status_x: X position for status symbol (default: 3)
        flag_x: X position for flag symbol (default: 5)
        use_colors: Whether to apply color formatting (default: True)
        is_selected: Whether the task is selected (affects coloring) (default: False)
    """
    # Print status indicator
    if task.get('status', False):
        if use_colors and not is_selected:
            stdscr.attron(curses.color_pair(6))  # Green
            stdscr.addstr(y, status_x, "✓")
            stdscr.attroff(curses.color_pair(6))
        else:
            stdscr.addstr(y, status_x, "✓")
    else:
        stdscr.addstr(y, status_x, " ")
    
    # Add space between status and flag
    stdscr.addstr(y, status_x + 1, " ")
    
    # Print flag indicator
    if task.get('flagged', False):
        if use_colors and not is_selected:
            stdscr.attron(curses.color_pair(7))  # Orange/Yellow
            stdscr.addstr(y, flag_x, "⚑")
            stdscr.attroff(curses.color_pair(7))
        else:
            stdscr.addstr(y, flag_x, "⚑")
    else:
        stdscr.addstr(y, flag_x, " ")
    
    # Add space after flag
    stdscr.addstr(y, flag_x + 1, " ")

def render_task(stdscr, task, y, is_selected=False, scroll_offset=0, max_x=0, 
               cursor_pos=None, is_edit_mode=False):
    """Core function to render a task with appropriate formatting"""
    if max_x == 0:
        max_x = stdscr.getmaxyx()[1]
    
    # Clear the row for custom rendering
    stdscr.move(y, 0)
    stdscr.clrtoeol()
    
    # Apply appropriate styling
    if is_selected:
        stdscr.attron(curses.color_pair(1))
    
    # Print task ID
    stdscr.addstr(y, 0, f"{task['id']:2d} ")
    
    # Print symbols (with colors appropriate for selected/non-selected)
    print_task_symbols(stdscr, task, y, 3, 5, use_colors=True, is_selected=is_selected)
    
    # Calculate date position and available text space
    date_str = task['date']
    base_length = 7  # Length of ID + status + flag area (indent)
    date_padding = 1  # Space between description and date - exact 1 char gap
    
    # Calculate date position 
    date_pos = max_x - len(date_str) - date_padding
    
    # Calculate available width for text - KEY FIX: subtract 1 more character for the gap
    text_length = len(task['description'])
    available_width = date_pos - base_length - 1  # -1 ensures the gap is preserved
    
    text_start_pos = base_length
    
    # In view mode, we just show what fits; in edit mode, we scroll
    if is_edit_mode:
        # Calculate visible portion of text based on scroll offset
        visible_start = scroll_offset
        visible_end = min(text_length, scroll_offset + available_width)
        visible_text = task['description'][visible_start:visible_end]
    else:
        # In view mode: truncate if too long without ellipsis
        if text_length > available_width:
            visible_text = task['description'][:available_width]
        else:
            visible_text = task['description']
            
        import todoism.settings as settings
        
        # Apply strike-through for completed tasks in view mode
        if task.get('status', False) and settings.get_strikethrough() and not is_edit_mode:
            # Apply strike-through using Unicode combining characters
            strikethrough_desc = ""
            for char in visible_text:
                strikethrough_desc += (char + "\u0336")  # Combine each character with strike
            visible_text = strikethrough_desc
    
    # Display text at calculated position
    if task.get('status', False) and not is_selected and not is_edit_mode:
        # Use dim text for completed tasks in view mode
        stdscr.attron(curses.A_DIM)  # Dim attribute
        stdscr.addstr(y, text_start_pos, visible_text)
        stdscr.attroff(curses.A_DIM)
    else:
        stdscr.addstr(y, text_start_pos, visible_text)
    
    # Print date with exactly one character gap
    stdscr.addstr(y, date_pos, date_str)
    
    # Turn off styling
    if is_selected:
        stdscr.attroff(curses.color_pair(1))
    
    # Calculate cursor position for edit mode
    if is_edit_mode and cursor_pos is not None:
        # Calculate position relative to visible text
        visible_cursor_pos = cursor_pos - scroll_offset
        
        if visible_cursor_pos >= 0 and visible_cursor_pos <= len(visible_text):
            # Normal case - cursor within visible text
            target_x = text_start_pos + visible_cursor_pos
        elif visible_cursor_pos < 0:
            # Cursor is before visible text
            target_x = text_start_pos
        else:
            # Cursor is after visible text
            target_x = text_start_pos + len(visible_text)
        
        # Make sure cursor stays within text area bounds
        target_x = min(target_x, date_pos - 1)  # -1 to respect the gap
        return target_x
    
    return None

def _print_task_core(stdscr, task, y, is_selected, max_x=0, is_edit_mode=False):
    """Core function to print a task with appropriate formatting"""
    return render_task(stdscr, task, y, is_selected, 0, max_x, None, is_edit_mode)

def print_task(stdscr, task, row, is_current, max_x):
    """Print a task with status indicators"""
    if is_current:
        print_task_selected(stdscr, task, row)
        return
    
    _print_task_core(stdscr, task, row, False, max_x)

def print_task_selected(stdscr, task, y):
    """Print a selected task with appropriate highlighting"""
    _print_task_core(stdscr, task, y, True)

def print_task_mode(stdscr, task, y, mode):
    """mode: add/edit"""
    if mode == edit_mode:
        # Pass is_edit_mode=True to prevent truncation with ellipsis
        _print_task_core(stdscr, task, y, True, 0, is_edit_mode=True)
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
    
    # Calculate percentage
    percent_value = (done_cnt/task_cnt)*100 if task_cnt > 0 else 0
    percent_text = f"({percent_value:.0f}%)"
    
    # Choose color based on percentage range
    if percent_value < 33:
        color_pair = 4  # Red for low completion
    elif percent_value < 67:
        color_pair = 3  # Yellow for medium completion
    else:
        color_pair = 2  # Green for high completion
    
    # Split the status into parts for coloring
    status_prefix = f"Done: {done_cnt}/{task_cnt} "
    
    # Format current date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime("%Y-%m-%d")
    time_str = current_datetime.strftime("%H:%M")
    datetime_str = f"{date_str} {time_str}"
    
    # Calculate center position
    total_len = len(status_prefix) + len(percent_text) + len(datetime_str) + 2  # +2 for spacing
    start_pos = (max_x - total_len) // 2
    
    # Clear only the top line
    stdscr.move(0, 0)
    stdscr.clrtoeol()
    
    # Print centered status with colored percentage and datetime
    stdscr.addstr(0, start_pos, status_prefix)
    stdscr.attron(curses.color_pair(color_pair))
    stdscr.addstr(0, start_pos + len(status_prefix), percent_text)
    stdscr.attroff(curses.color_pair(color_pair))
    stdscr.addstr(0, start_pos + len(status_prefix) + len(percent_text) + 2, datetime_str)

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
