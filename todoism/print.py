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

def print_msg(stdscr, msg, x_offset=16, highlight=False):
    """Print a message box with proper centering in the task area with optional highlighting"""
    lines = msg.split('\n')
    width = len(lines[1])
    max_y, max_x = stdscr.getmaxyx()
    
    # Calculate available width for task area (total width minus sidebar)
    available_width = max_x - x_offset
    
    # Calculate center position within the available task area
    center_offset = (available_width - width) // 2
    
    # Clear the task area before printing
    for i in range(1, max_y):
        stdscr.move(i, x_offset)
        stdscr.clrtoeol()
    
    # Apply highlighting if requested
    if highlight:
        stdscr.attron(curses.color_pair(1))
    
    # Print each line separately at the calculated position
    for i, line in enumerate(lines):
        y = i + 1  # Start at row 1 (row 0 is status bar)
        if y < max_y and line.strip():  # Only print non-empty lines and check bounds
            # Position cursor at sidebar edge + centering offset
            stdscr.move(y, x_offset + center_offset)
            # Print the line directly
            stdscr.addstr(line)
    
    # Remove highlighting if it was applied
    if highlight:
        stdscr.attroff(curses.color_pair(1))
    
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
            stdscr.addstr(y, status_x, '✓')
            stdscr.attroff(curses.color_pair(6))
        else:
            stdscr.addstr(y, status_x, '✓')
    else:
        stdscr.addstr(y, status_x, ' ')
    
    # Add space between status and flag
    stdscr.addstr(y, status_x + 1, ' ')
    
    # Print flag indicator
    if task.get('flagged', False):
        if use_colors and not is_selected:
            stdscr.attron(curses.color_pair(7))  # Orange/Yellow
            stdscr.addstr(y, flag_x, '⚑')
            stdscr.attroff(curses.color_pair(7))
        else:
            stdscr.addstr(y, flag_x, '⚑')
    else:
        stdscr.addstr(y, flag_x, ' ')
    
    # Add space after flag
    stdscr.addstr(y, flag_x + 1, ' ')

def render_task(stdscr, task, y, is_selected=False, scroll_offset=0, max_x=0, 
               cursor_pos=None, is_edit_mode=False, is_sidebar=False):
    """Render a task with proper formatting and positioning"""
    if max_x == 0:
        max_x = stdscr.getmaxyx()[1]
    
    # Determine position calculations based on sidebar mode
    if is_sidebar:
        # Sidebar positioning - no offset
        sidebar_width = 0  # No sidebar offset needed
        base_indent = 1    # 1-space indent from left edge (matching print_category)
        
        # Clear the row for custom rendering
        stdscr.move(y, 0)
        # stdscr.clrtoeol()
        
        # No ID display anymore
        
        text_start_pos = base_indent
        total_indent = base_indent
        date_str = ""
        date_pos = 15  # End of sidebar
    else:
        # Task area positioning - include sidebar offset
        sidebar_width = 16  # 15 chars + 1 for separator
        base_indent = 7    # Length of ID + status + flag area
        
        # Clear the row for custom rendering
        stdscr.move(y, sidebar_width)
        stdscr.clrtoeol()
        
        # Print separator at correct position
        stdscr.addstr(y, 15, "│")
        
        if is_selected:
            stdscr.attron(curses.color_pair(1))
        
        # Print task ID with offset
        stdscr.addstr(y, sidebar_width, f"{task['id']:2d} ")
        
        # Print symbols with offset
        print_task_symbols(stdscr, task, y, sidebar_width + 3, sidebar_width + 5, use_colors=True, is_selected=is_selected)
        
        # Calculate date position and available text space
        date_str = task['date']
        date_padding = 1  # Space between description and date
        date_pos = max_x - len(date_str) - date_padding
        
        text_start_pos = sidebar_width + base_indent  # Combined offset
        total_indent = text_start_pos
    
    # Calculate available width for text
    available_width = date_pos - total_indent - (0 if is_sidebar else 1)
    
    # In view mode, we just show what fits; in edit mode, we scroll
    text_length = len(task['description'])
    if is_edit_mode:
        # Calculate visible portion of text based on scroll offset
        visible_start = scroll_offset
        visible_end = min(text_length, scroll_offset + available_width)
        visible_text = task['description'][visible_start:visible_end]
    else:
        # In view mode: truncate if too long
        if text_length > available_width:
            visible_text = task['description'][:available_width]
        else:
            visible_text = task['description']
            
        import todoism.settings as settings
        
        # Apply strike-through for completed tasks in view mode
        if task.get('status', False) and settings.get_strikethrough() and not is_edit_mode:
            strikethrough_desc = ""
            for char in visible_text:
                strikethrough_desc += (char + "\u0336")
            visible_text = strikethrough_desc
    
    # Display text at calculated position
    if task.get('status', False) and not is_selected and not is_edit_mode:
        stdscr.attron(curses.A_DIM)
        stdscr.addstr(y, text_start_pos, visible_text)
        stdscr.attroff(curses.A_DIM)
    else:
        stdscr.addstr(y, text_start_pos, visible_text)
    
    for i in range(available_width - len(visible_text)):
        stdscr.addstr(' ')
    
    # Print date with exactly one character gap (only for tasks, not sidebar)
    if not is_sidebar and date_str:
        stdscr.addstr(y, date_pos, date_str)
    
    # Turn off styling
    if is_selected:
        stdscr.attroff(curses.color_pair(1))
    
    # Calculate cursor position for edit mode
    if is_edit_mode and cursor_pos is not None:
        visible_cursor_pos = cursor_pos - scroll_offset
        
        if visible_cursor_pos >= 0 and visible_cursor_pos <= len(visible_text):
            target_x = text_start_pos + visible_cursor_pos
        elif visible_cursor_pos < 0:
            target_x = text_start_pos
        else:
            target_x = text_start_pos + len(visible_text)
        
        target_x = min(target_x, date_pos - (0 if is_sidebar else 1))
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
    start_pos = (max_x - total_len - 16) // 2 + 16
    
    # Save character at the separator position
    separator_char = None
    try:
        # Try to read the current character at separator position
        separator_char = stdscr.inch(0, 15) & curses.A_CHARTEXT
    except curses.error:
        # Handle edge case when reading might fail
        pass
        
    # Clear only the top line
    stdscr.move(0, 0)
    stdscr.clrtoeol()
    
    # Print centered status with colored percentage and datetime
    stdscr.addstr(0, start_pos, status_prefix)
    stdscr.attron(curses.color_pair(color_pair))
    stdscr.addstr(0, start_pos + len(status_prefix), percent_text)
    stdscr.attroff(curses.color_pair(color_pair))
    stdscr.addstr(0, start_pos + len(status_prefix) + len(percent_text) + 2, datetime_str)
    
    # CRITICAL FIX: Restore the separator character at position (0,15)
    try:
        stdscr.addstr(0, 15, "│")
    except curses.error:
        # Handle edge case when terminal is too small
        pass

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

def print_sidebar(stdscr, categories, current_category_id, start_index, max_height, has_focus):
    """Print the category sidebar"""
    # Set sidebar width
    sidebar_width = 15
    
    # Clear sidebar area
    for y in range(1, max_height + 1):
        stdscr.move(y, 0)
        stdscr.clrtoeol()  # Use clrtoeol() for consistent clearing
    
    # Print visible categories
    visible_categories = categories[start_index:start_index + max_height]
    for i, category in enumerate(visible_categories):
        row = i + 1  # Start from row 1 (row 0 is for status bar)
        is_selected = category['id'] == current_category_id
        print_category(stdscr, category, row, is_selected, has_focus)
    
    # Print vertical separator
    for y in range(0, max_height + 1):
        stdscr.addstr(y, sidebar_width, "│")

def print_category(stdscr, category, y, is_selected=False, has_focus=False):
    """Print a single category in the sidebar"""
    # Set format based on selection and focus
    if is_selected and has_focus:
        stdscr.attron(curses.color_pair(1))  # Use the same highlight as tasks
    elif is_selected and not has_focus:
        stdscr.attron(curses.A_BOLD)
    
    # Calculate available width for category name
    sidebar_width = 15
    name_width = sidebar_width - 1  # Just 1 character for spacing now
    
    # Don't display the ID number, just offset the name by 1 space from the left edge
    
    # Truncate category name if too long
    if len(category['name']) > name_width:
        display_name = category['name'][:name_width-1] + "…"
    else:
        display_name = category['name']
    
    # Display name with 1 character offset from left edge
    stdscr.addstr(y, 1, display_name)
    
    for i in range(name_width - len(display_name)):
        stdscr.addstr(' ')
    
    # Reset attributes
    if is_selected and has_focus:
        stdscr.attroff(curses.color_pair(1))
    elif is_selected and not has_focus:
        stdscr.attroff(curses.A_BOLD)

def print_main_view_with_sidebar(stdscr, done_cnt, task_cnt, tasks, current_id, 
                               start, end, categories, current_category_id, 
                               category_start_index, sidebar_has_focus):
    """Print the complete UI with sidebar and task list"""
    # Get max visible height
    max_y, _ = stdscr.getmaxyx()
    max_height = max_y - 1  # Account for status bar
    
    # Print status bar first
    print_status_bar(stdscr, done_cnt, task_cnt)
    
    # Print sidebar
    print_sidebar(stdscr, categories, current_category_id, 
                 category_start_index, max_height, sidebar_has_focus)
    
    # Print tasks or empty message
    if task_cnt == 0:
        # Clear task area
        for y in range(1, max_height + 1):
            stdscr.move(y, 16)
            stdscr.clrtoeol()
        # Print empty message with highlighting when task area has focus
        print_msg(stdscr, empty_msg, 16, highlight=(not sidebar_has_focus))
    else:
        print_tasks_with_offset(stdscr, tasks, current_id, start, end, 16)

def print_tasks_with_offset(stdscr, task_list, current_id, start, end, x_offset=0):
    """Print tasks with horizontal offset to accommodate sidebar"""
    max_y, _ = stdscr.getmaxyx()
    
    # Clear task area first
    for y in range(1, min(end - start + 2, max_y)):
        stdscr.move(y, x_offset)
        stdscr.clrtoeol()
    
    # Only print if we have tasks and a valid start index
    if task_list and start > 0:
        for i, task in enumerate(task_list[start - 1:end]):
            row = i + 1  # +1 due to status bar
            display_id = i + start  # Sequential display ID (1, 2, 3, etc.)
            
            if i + start == current_id:
                # Selected task
                print_task_selected_with_offset(stdscr, task, row, x_offset, display_id)
            else:
                # Normal task
                print_task_with_offset(stdscr, task, row, False, x_offset, display_id)

def print_task_with_offset(stdscr, task, row, is_selected, x_offset=0, display_id=None):
    """Print a task with horizontal offset and optional display ID override"""
    # Calculate available width for text
    max_y, max_x = stdscr.getmaxyx()
    
    # Use display_id if provided, otherwise use task's actual ID
    id_to_show = display_id if display_id is not None else task['id']
    
    # Print task ID
    stdscr.addstr(row, x_offset, f"{id_to_show:2d} ")
    
    # Rest of the function remains the same
    print_task_symbols(stdscr, task, row, 
                      status_x=x_offset + 3, 
                      flag_x=x_offset + 5,
                      use_colors=True,
                      is_selected=is_selected)
    
    # Calculate date position and available text space
    date_str = task['date']
    date_padding = 1
    date_pos = max_x - len(date_str) - date_padding
    
    # Calculate available space for text
    indent = 7  # ID + status + flag area
    total_indent = x_offset + indent
    available_width = date_pos - total_indent
    
    # Handle text display
    text = task['description']
    if len(text) > available_width:
        visible_text = text[:available_width]
    else:
        visible_text = text  # FIX: Properly assign text to visible_text
        
    # Apply strikethrough if needed
    import todoism.settings as settings
    if task.get('status', False) and settings.get_strikethrough() and not is_selected:
        strikethrough_desc = ""
        for char in visible_text:
            strikethrough_desc += (char + "\u0336")
        visible_text = strikethrough_desc
    
    # Display text at calculated position with proper styling
    if task.get('status', False) and not is_selected:
        stdscr.attron(curses.A_DIM)
        stdscr.addstr(row, total_indent, visible_text)
        stdscr.attroff(curses.A_DIM)
    else:
        stdscr.addstr(row, total_indent, visible_text)
    
    for i in range(available_width - len(visible_text)):
        stdscr.addstr(' ')
    
    # Print date
    stdscr.addstr(row, date_pos, date_str)

def print_task_selected_with_offset(stdscr, task, row, x_offset=0, display_id=None):
    """Print a selected task with offset"""
    stdscr.attron(curses.color_pair(1))
    print_task_with_offset(stdscr, task, row, True, x_offset, display_id)
    stdscr.attroff(curses.color_pair(1))

def ensure_separator_visible(stdscr, max_height=None):
    """Ensure the vertical separator is visible across the entire height"""
    if max_height is None:
        max_y, _ = stdscr.getmaxyx()
        max_height = max_y
    
    # Draw separator at each row
    for y in range(max_height):
        try:
            stdscr.addstr(y, 15, '│')
        except curses.error:
            # Handle edge case when writing to bottom-right corner
            pass
    
    # Force immediate refresh for the separator
    stdscr.noutrefresh()
