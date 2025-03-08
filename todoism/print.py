import curses
import todoism.settings as st
from datetime import datetime

add_mode  = 0
edit_mode = 1

help_msg =  '''
┌──────────────────────────────────────────────────┐
│                                                  │
│   Short commands:                                │
│   a - Create new task/category                   │
│   d - Mark task as done                          │
│   e - Edit task/category                         │
│   f - Mark task as flagged                       │
│   q - Quit this help message/todoism             │
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
│   Other key bindings:                            │
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
└──────────────────────────────────────────────────┘
'''

empty_msg = f'''
┌──────────────────────────────────────────────────────┐
│       Hmm, it seems there are no active tasks        │
│     Take a break, or create some to get busy :)      │
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
    
    # Ensure we have minimum required space
    if max_y < 2 or max_x < x_offset + 1:
        return
    
    # Calculate available width for task area (total width minus sidebar)
    available_width = max(0, max_x - x_offset)
    
    # Calculate center position within the available task area
    # Ensure center_offset is never negative
    center_offset = max(0, (available_width - width) // 2)
    
    # Clear the task area before printing
    for i in range(1, max_y - 1):  # Leave the bottom row for bottom frame
        try:
            stdscr.move(i, x_offset)
            stdscr.clrtoeol()
        except curses.error:
            continue
    
    # Apply highlighting if requested
    if highlight:
        stdscr.attron(curses.color_pair(1))
    
    # Print each line separately at the calculated position
    for i, line in enumerate(lines):
        y = i + 1  # Start at row 1 (row 0 is status bar)
        if y < max_y - 1 and line.strip():  # Only print non-empty lines and check bounds
            try:
                # Position cursor at sidebar edge + centering offset
                stdscr.move(y, x_offset + center_offset)
                # Print the line directly, truncating if necessary
                if x_offset + center_offset + len(line) > max_x:
                    # Truncate line to fit available space
                    available_space = max_x - (x_offset + center_offset)
                    if available_space > 0:
                        stdscr.addstr(line[:available_space])
                else:
                    stdscr.addstr(line)
            except curses.error:
                continue
    
    # Remove highlighting if it was applied
    if highlight:
        stdscr.attroff(curses.color_pair(1))
    
    # Draw the right frame for each line
    for y in range(1, max_y - 1):
        try:
            stdscr.addstr(y, max_x - 1, '│')
        except curses.error:
            continue
    
    # Draw the bottom frame if there's enough space
    if max_y > 2:
        try:
            stdscr.addstr(max_y - 1, x_offset - 1, "┴")
            # Draw horizontal line only if there's space
            remaining_width = max_x - x_offset - 1
            if remaining_width > 0:
                for x in range(x_offset, max_x - 2):
                    stdscr.addstr(max_y - 1, x, "─")
                stdscr.addstr(max_y - 1, max_x - 2, "┘")
                stdscr.insstr(max_y - 1, max_x - 2, "─")
        except curses.error:
            pass
    
    # Update specific areas instead of full refresh
    stdscr.noutrefresh()
    curses.doupdate()

def print_version():
    print("todoism version 1.21.2")

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
        base_indent = 2    # Changed from 1 to 2 spaces (1 for left border + 1 for spacing)
        
        # Clear the row for custom rendering
        stdscr.move(y, 0)
        # Draw left frame
        stdscr.addstr(y, 0, "│")
        
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
        
        # Print separator at correct position - check if this is the top row
        # Turn off highlight before drawing frame
        if is_selected:
            stdscr.attroff(curses.color_pair(1))
        char = '┬' if y == 0 else '│'
        stdscr.addstr(y, 15, char)
        if is_selected:
            stdscr.attron(curses.color_pair(1))
        
        # Print task ID with offset
        stdscr.addstr(y, sidebar_width, f"{task['id']:2d} ")
        
        # Print symbols with offset
        print_task_symbols(stdscr, task, y, sidebar_width + 3, sidebar_width + 5, use_colors=True, is_selected=is_selected)
        
        # Calculate date position and available text space
        date_str = task['date']
        date_padding = 1  # Space between description and date
        date_pos = max_x - len(date_str) - date_padding - 1  # Account for right frame
        
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
    
    # Print date with exactly one character gap to right
    if not is_sidebar and date_str:
        stdscr.addstr(y, date_pos, date_str)
        if is_selected:
            stdscr.addstr(y, date_pos + len(date_str), ' ')
    
    # Print right frame without highlight
    if not is_sidebar:
        if is_selected:
            stdscr.attroff(curses.color_pair(1))
        try:
            stdscr.addstr(y, max_x - 1, '│')
        except curses.error:
            pass
        if is_selected:
            stdscr.attron(curses.color_pair(1))
    
    # Calculate cursor position for edit mode
    if is_edit_mode and cursor_pos is not None:
        visible_cursor_pos = cursor_pos - scroll_offset
        
        if visible_cursor_pos >= 0 and visible_cursor_pos <= len(visible_text):
            target_x = text_start_pos + visible_cursor_pos
        elif visible_cursor_pos < 0:
            target_x = text_start_pos
        else:
            target_x = text_start_pos + len(visible_text)
        
        if is_sidebar:
            # Hard limit for sidebar - never allow cursor beyond column 14
            target_x = min(target_x, 14)
        else:
            # Normal limit for task area
            target_x = min(target_x, date_pos - (0 if is_sidebar else 1))
        
        return target_x
    
    return None


def print_status_bar(stdscr, done_cnt, task_cnt):
    """Print centered status bar with progress, percentage, date and time"""
    max_y, max_x = stdscr.getmaxyx()
    
    # Reset all attributes at the start
    stdscr.attroff(curses.A_BOLD | curses.A_DIM | curses.color_pair(1) | 
                   curses.color_pair(2) | curses.color_pair(3) | curses.color_pair(4))
    
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
    status_prefix = f"┤Done: {done_cnt}/{task_cnt} "
    
    # Format current date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime("%Y-%m-%d")
    time_str = current_datetime.strftime("%H:%M")
    datetime_str = f"{date_str} {time_str}├"
    
    # Calculate center position
    total_len = len(status_prefix) + len(percent_text) + len(datetime_str) + 2  # +2 for spacing
    start_pos = (max_x - total_len - 16) // 2 + 16
    
    # Clear only the top line
    stdscr.move(0, 0)
    stdscr.clrtoeol()
    
    # Draw horizontal frame across entire top line
    for x in range(max_x - 1):  # Stop one char before the end
        # Skip position 0 (will be ┌) and position 15 (will be ┬)
        if x != 0 and x != 15:
            try:
                stdscr.addstr(0, x, "─")
            except curses.error:
                pass
    
    # Add the corners and junctions without highlight
    try:
        # Left corner
        stdscr.addstr(0, 0, "┌")
        # T-junction at position (0, 15) where vertical meets horizontal
        stdscr.addstr(0, 15, "┬")
        # Right corner
        stdscr.addstr(0, max_x - 1, "┐")
    except curses.error:
        pass
    
    # Print centered status with colored percentage and datetime
    stdscr.addstr(0, start_pos, status_prefix)
    stdscr.attron(curses.color_pair(color_pair))
    stdscr.addstr(0, start_pos + len(status_prefix), percent_text)
    stdscr.attroff(curses.color_pair(color_pair))
    stdscr.addstr(0, start_pos + len(status_prefix) + len(percent_text) + 2, datetime_str)
    
    # Ensure all attributes are reset at the end
    stdscr.attroff(curses.A_BOLD | curses.A_DIM | curses.color_pair(1) | 
                   curses.color_pair(2) | curses.color_pair(3) | curses.color_pair(4))


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
    max_y, max_x = stdscr.getmaxyx()
    
    # Clear sidebar area
    for y in range(1, max_height + 1):
        stdscr.move(y, 0)
        stdscr.clrtoeol()  # Use clrtoeol() for consistent clearing
    
    # Add left vertical frame for each row
    for y in range(1, max_y - 1):
        try:
            stdscr.addstr(y, 0, "│")
        except curses.error:
            pass
    stdscr.addstr(max_y - 1, 0, "└")
    
    for x in range(1, sidebar_width):
        stdscr.addstr(max_y - 1, x, "─")
    
    # Print visible categories
    visible_categories = categories[start_index:start_index + max_height]
    for i, category in enumerate(visible_categories):
        row = i + 1  # Start from row 1 (row 0 is for status bar)
        is_selected = category['id'] == current_category_id
        print_category(stdscr, category, row, is_selected, has_focus)
    
    # Print vertical separator
    for y in range(0, max_y - 1):
        # Use T-junction for top row
        char = '┬' if y == 0 else '│'
        stdscr.addstr(y, sidebar_width, char)
    
    # draw bottom frame
    stdscr.addstr(max_y - 1, sidebar_width, "┴")
    
    for x in range(sidebar_width + 1, max_x - 2):
        stdscr.addstr(max_y - 1, x, "─")

def print_category(stdscr, category, y, is_selected=False, has_focus=False):
    """Print a single category in the sidebar with fixed width"""
    # Set format based on selection and focus
    if is_selected and has_focus:
        stdscr.attron(curses.color_pair(1))  # Use the same highlight as tasks
    elif is_selected and not has_focus:
        curses.init_pair(8, st.get_color_selected(), curses.COLOR_BLACK)
        stdscr.attron(curses.color_pair(8))
        stdscr.attron(curses.A_BOLD)
    
    # Import the max category name length
    import todoism.category as cat
    
    # Calculate available width for category name
    sidebar_width = 15
    name_width = sidebar_width - 2  # 2 spaces for indentation (1 for left border + 1 for spacing)
    
    if is_selected:
        stdscr.addstr(y, 1, ' ')
    
    # Always show the full name (it's already limited by MAX_CATEGORY_NAME_LENGTH)
    # If it's somehow longer, truncate it with an ellipsis
    if len(category['name']) > name_width:
        display_name = category['name'][:name_width-1] + "…"
    else:
        display_name = category['name']
    
    # Display name with fixed width - now at position 2 (after the left frame)
    stdscr.addstr(y, 2, display_name)
    
    # Fill remaining space with spaces to ensure fixed width
    padding = name_width - len(display_name)
    if padding > 0:
        stdscr.addstr(' ' * padding)
    
    # Reset attributes
    if is_selected and has_focus:
        stdscr.attroff(curses.color_pair(1))
    elif is_selected and not has_focus:
        stdscr.attroff(curses.color_pair(8))
        stdscr.attroff(curses.A_BOLD)

def print_main_view_with_sidebar(stdscr, done_cnt, task_cnt, tasks, current_id, 
                               start, end, categories, current_category_id, 
                               category_start_index, sidebar_has_focus):
    """Print the complete UI with sidebar and task list"""
    # Get max visible height
    max_y, _ = stdscr.getmaxyx()
    # Reduce max_height by 1 to account for bottom frame
    max_height = max_y - 2  # -1 for status bar, -1 for bottom frame
    
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
    max_y, max_x = stdscr.getmaxyx()
    
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
    
    max_y, max_x = stdscr.getmaxyx()
    for y in range(len(task_list) if len(task_list) > 0 else 1, max_y - 1):
        stdscr.addstr(y, max_x - 1, "│")
    # https://stackoverflow.com/questions/7063128/last-character-of-a-window-in-python-curses
    # Special trick for last char error in cursor window
    stdscr.addstr(max_y-1, max_x - 2, "┘")
    stdscr.insstr(max_y-1, max_x - 2, "─")

    
    
def print_task_with_offset(stdscr, task, row, is_selected, x_offset=0, display_id=None):
    """Print a task with horizontal offset and optional display ID override"""
    # Calculate available width for text
    max_y, max_x = stdscr.getmaxyx()
    
    # Use display_id if provided, otherwise use task's actual ID
    id_to_show = display_id if display_id is not None else task['id']
    
    if not is_selected:
        stdscr.attroff(curses.color_pair(1))

    # Print task ID
    stdscr.addstr(row, x_offset, f"{id_to_show:2d} ")
    
    # Print task symbols
    print_task_symbols(stdscr, task, row, 
                      status_x=x_offset + 3, 
                      flag_x=x_offset + 5,
                      use_colors=not is_selected,
                      is_selected=is_selected)
    
    # Calculate positions with right frame
    right_frame_pos = max_x - 1
    date_str = task['date']
    date_pos = right_frame_pos - len(date_str) - 1  # Only 1 char gap from right frame
    
    # Calculate available space for text
    indent = 7  # ID + status + flag area
    total_indent = x_offset + indent
    available_width = date_pos - total_indent - 1  # Space for gap before date
    
    # Handle text display
    text = task['description']
    if len(text) > available_width:
        visible_text = text[:available_width]
    else:
        visible_text = text
        
    # Apply strikethrough if needed
    import todoism.settings as settings
    if task.get('status', False) and settings.get_strikethrough() and not is_selected:
        strikethrough_desc = ""
        for char in visible_text:
            strikethrough_desc += (char + "\u0336")
        visible_text = strikethrough_desc
    
    # Display text at calculated position with proper styling
    if is_selected:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(row, total_indent, visible_text)
        # Fill remaining space with spaces
        for i in range(available_width - len(visible_text) + 1):
            stdscr.addstr(' ')
        stdscr.addstr(row, date_pos, date_str)
        stdscr.attroff(curses.color_pair(1))
    else:
        if task.get('status', False):
            stdscr.attron(curses.A_DIM)
        stdscr.addstr(row, total_indent, visible_text)
        # Fill remaining space with spaces
        for i in range(available_width - len(visible_text)):
            stdscr.addstr(' ')
        # Print date
        stdscr.addstr(row, date_pos, date_str)
        if task.get('status', False):
            stdscr.attroff(curses.A_DIM)
    
    try:
        if is_selected:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(row, right_frame_pos - 1, ' ')
            stdscr.attroff(curses.color_pair(1))
        stdscr.addstr(row, right_frame_pos, '│')
    except curses.error:
        pass


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
    
    # Draw left frame
    for y in range(max_height):
        try:
            # Use corner for top row, vertical bar for others
            char = '┌' if y == 0 else '│'
            stdscr.addstr(y, 0, char)
        except curses.error:
            pass
    
    # Draw right separator (between sidebar and main area)
    for y in range(max_height):
        try:
            # Use T-junction character for the top row, vertical bar for others
            char = '┬' if y == 0 else '│'
            stdscr.addstr(y, 15, char)
        except curses.error:
            pass
    
    # Draw right frame
    for y in range(max_height):
        try:
            # Use corner for top row, vertical bar for others
            char = '┐' if y == 0 else '│'
            stdscr.addstr(y, stdscr.getmaxyx()[1] - 1, char)
        except curses.error:
            pass
    
    # Force immediate refresh for the separator
    stdscr.noutrefresh()
    curses.doupdate()
