import curses
import todoism.strikethrough as st
import todoism.message as msg
import todoism.color as clr
import todoism.category as cat
import todoism.preference as pref
from datetime import datetime

add_mode  = 0
edit_mode = 1

# Function to display centered messages
def print_msg_center(stdscr, message, color_pair=0, highlight_line=-1):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    lines = message.strip().split("\n")
    start_y = max(0, (max_y - len(lines)) // 2)
    
    for i, line in enumerate(lines):
        if line.strip():  # Only print non-empty lines
            start_x = max(0, (max_x - len(line)) // 2)
            if i == highlight_line and color_pair > 0:
                stdscr.attron(curses.color_pair(color_pair))
                stdscr.addstr(start_y + i, start_x, line)
                stdscr.attroff(curses.color_pair(color_pair))
            else:
                stdscr.addstr(start_y + i, start_x, line)
    
    stdscr.refresh()

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
    clear_task_panel(stdscr, max_y)
    
    # Apply highlighting if requested
    if highlight:
        stdscr.attron(curses.color_pair(clr.selection_color_pair_num))
    
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
        stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))
    
    # Draw the right frame for each line
    print_right_frame(stdscr, max_y, max_x)

    # Use noutrefresh() instead of refresh() for better performance
    # when multiple updates happen in sequence
    stdscr.noutrefresh()
    curses.doupdate()

def print_version():
    print("todoism version 1.21.3")

def print_task_symbols(stdscr, task, y, flag_x=3, status_x=5, use_colors=True, is_selected=False):
    """Print task flag and status symbols with appropriate colors
    
    Args:
        stdscr: The curses window
        task: The task data dictionary
        y: The row position
        flag_x: X position for flag symbol (default: 3)
        status_x: X position for status symbol (default: 5)
        use_colors: Whether to apply color formatting (default: True)
        is_selected: Whether the task is selected (affects coloring) (default: False)
    """
    if task.get('flagged', False):
        if use_colors and not is_selected:
            flag_color = clr.get_color_pair_num_by_str("red")
            stdscr.attron(curses.color_pair(flag_color))
            stdscr.addstr(y, flag_x, '⚑')
            stdscr.attroff(curses.color_pair(flag_color))
        else:
            stdscr.addstr(y, flag_x, '⚑')
    else:
        stdscr.addstr(y, flag_x, ' ')
    
    # Add space between flag and status
    stdscr.addstr(y, flag_x + 1, ' ')
    
    # Print status indicator second
    if task.get('status', False):
        if use_colors and not is_selected:
            check_color = clr.get_color_pair_num_by_str("green")
            stdscr.attron(curses.color_pair(check_color))
            stdscr.addstr(y, status_x, '✓')
            stdscr.attroff(curses.color_pair(check_color))
        else:
            stdscr.addstr(y, status_x, '✓')
    else:
        stdscr.addstr(y, status_x, ' ')
    
    stdscr.addstr(y, status_x + 1, ' ')

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
            stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))
        stdscr.addstr(y, 15, '│')
        if is_selected:
            stdscr.attron(curses.color_pair(clr.selection_color_pair_num))
        
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
        if text_length > available_width:
            visible_start = scroll_offset
            visible_end = min(text_length, scroll_offset + available_width)
            if visible_end == text_length:
                visible_text = task['description'][text_length - available_width:]
            else:
                visible_text = task['description'][visible_start:visible_end]
        else:
            visible_text = task['description']
        # Apply strike-through for completed tasks in view mode
        if task.get('status', False) and st.get_strikethrough() and not is_edit_mode:
            strikethrough_desc = ""
            for char in visible_text:
                strikethrough_desc += (char + "\u0336")
            visible_text = strikethrough_desc
    
    highlight_trailing_blank_space = 0
    # Display text at calculated position
    if task.get('status', False) and not is_selected and not is_edit_mode:
        stdscr.attron(curses.A_DIM)
        stdscr.addstr(y, text_start_pos, visible_text)
        stdscr.attroff(curses.A_DIM)
        highlight_trailing_blank_space = available_width - len(visible_text)
    else:
        highlight_trailing_blank_space = available_width - len(visible_text) + 1
        stdscr.addstr(y, text_start_pos, visible_text)
    
    for i in range(highlight_trailing_blank_space):
        stdscr.addstr(' ')
    
    # Print date with exactly one character gap to right
    if not is_sidebar and date_str:
        stdscr.addstr(y, date_pos, date_str)
        if is_selected:
            stdscr.addstr(y, date_pos + len(date_str), ' ')
    
    # Print right frame without highlight
    if not is_sidebar:
        if is_selected:
            stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))
        try:
            stdscr.addstr(y, max_x - 1, '│')
        except curses.error:
            pass
        if is_selected:
            stdscr.attron(curses.color_pair(clr.selection_color_pair_num))
    
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
    stdscr.attroff(curses.A_BOLD | curses.A_DIM | curses.color_pair(clr.selection_color_pair_num) | 
                   curses.color_pair(2) | curses.color_pair(3) | curses.color_pair(4))
    
    # Calculate percentage
    percent_value = (done_cnt/task_cnt)*100 if task_cnt > 0 else 0
    percent_text = f"({percent_value:.0f}%)"
    
    # Choose color based on percentage range
    if percent_value < 33:
        color_pair = clr.get_color_pair_num_by_str("red")
    elif percent_value < 67:
        color_pair = clr.get_color_pair_num_by_str("yellow")
    else:
        color_pair = clr.get_color_pair_num_by_str("green")
    
    # Split the status into parts for coloring
    status_prefix = f"┤Done: {done_cnt}/{task_cnt} "
    
    current_date_format = pref.get_date_format()
    current_datetime = datetime.now()
    date_str = ""
    if current_date_format == "Y-M-D":
        date_str = current_datetime.strftime("%Y-%m-%d")
    elif current_date_format == "D-M-Y":
        date_str = current_datetime.strftime("%d-%m-%Y")
    elif current_date_format == "M-D-Y":
        date_str = current_datetime.strftime("%m-%d-%Y")
    
    time_str = current_datetime.strftime("%H:%M")
    datetime_str = f"{date_str} {time_str}├"
    
    # Calculate center position
    total_len = len(status_prefix) + len(percent_text) + len(datetime_str) + 2  # +2 for spacing
    start_pos = (max_x - total_len - 16) // 2 + 16
    
    # Clear only the top line
    stdscr.move(0, 0)
    stdscr.clrtoeol()
    
    print_top_left_corner(stdscr)
    print_top_frame(stdscr, max_x)
    print_seperator_connector_top(stdscr)
    print_top_right_corner(stdscr, max_x)
    
    # Print centered status with colored percentage and datetime
    stdscr.addstr(0, start_pos, status_prefix)
    stdscr.attron(curses.color_pair(color_pair))
    stdscr.addstr(0, start_pos + len(status_prefix), percent_text)
    stdscr.attroff(curses.color_pair(color_pair))
    stdscr.addstr(0, start_pos + len(status_prefix) + len(percent_text) + 2, datetime_str)
    
    # Ensure all attributes are reset at the end
    stdscr.attroff(curses.A_BOLD | curses.A_DIM | curses.color_pair(clr.selection_color_pair_num) | 
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
    
    print_left_frame(stdscr, max_y)
    print_bottom_left_corner(stdscr, max_y)
    
    for x in range(1, sidebar_width):
        stdscr.addstr(max_y - 1, x, "─")
    
    # Print visible categories
    visible_categories = categories[start_index:start_index + max_height]
    for i, category in enumerate(visible_categories):
        row = i + 1  # Start from row 1 (row 0 is for status bar)
        is_selected = category['id'] == current_category_id
        print_category(stdscr, category, row, is_selected, has_focus)

    print_seperator_connector_top(stdscr)
    print_sidebar_task_panel_separator(stdscr, max_y)
    print_seperator_connector_bottom(stdscr, max_y)
    
    for x in range(sidebar_width + 1, max_x - 2):
        stdscr.addstr(max_y - 1, x, "─")

def print_category(stdscr, category, y, is_selected=False, has_focus=False):
    """Print a single category in the sidebar with fixed width"""
    # Set format based on selection and focus
    if is_selected and has_focus:
        stdscr.attron(curses.color_pair(clr.selection_color_pair_num))  # Use the same highlight as tasks
    elif is_selected and not has_focus:
        stdscr.attron(curses.color_pair(clr.get_current_color_pair_number()))
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
        stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))
    elif is_selected and not has_focus:
        stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))
        stdscr.attroff(curses.A_BOLD)

def print_main_view_with_sidebar(stdscr, done_cnt, task_cnt, tasks, current_task_id, 
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
        print_msg(stdscr, msg.empty_msg, 16, highlight=(not sidebar_has_focus))
    else:
        print_tasks_with_offset(stdscr, tasks, current_task_id, current_category_id, start, end, 16)
    
    # Use a single refresh at the end instead of multiple refreshes in each function
    stdscr.noutrefresh()
    curses.doupdate()

def print_tasks_with_offset(stdscr, task_list, current_task_id, current_category_id, start, end, x_offset=0):
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
            
            if i + start == current_task_id:
                # Selected task
                print_task_selected_with_offset(stdscr, task, row, x_offset, display_id, current_category_id)
            else:
                # Normal task
                print_task_with_offset(stdscr, task, row, False, x_offset, display_id, current_category_id)
    
    max_y, max_x = stdscr.getmaxyx()
    for y in range(len(task_list) if len(task_list) > 0 else 1, max_y - 1):
        stdscr.addstr(y, max_x - 1, "│")
    # https://stackoverflow.com/questions/7063128/last-character-of-a-window-in-python-curses
    # Special trick for last char error in cursor window
    stdscr.addstr(max_y - 1, max_x - 2, "┘")
    stdscr.insstr(max_y - 1, max_x - 2, "─")

    
    
def print_task_with_offset(stdscr, task, row, is_selected, x_offset=0, display_id=None, current_category_id=0):
    """Print a task with horizontal offset and optional display ID override"""
    # Calculate available width for text
    max_y, max_x = stdscr.getmaxyx()
    
    # Use display_id if provided, otherwise use task's actual ID
    id_to_show = display_id if display_id is not None else task['id']
    
    if not is_selected:
        stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))

    # Print task ID
    stdscr.addstr(row, x_offset, f"{id_to_show:2d} ")
    
    # Print task symbols with swapped positions
    print_task_symbols(stdscr, task, row, 
                      flag_x=x_offset + 3, 
                      status_x=x_offset + 5,
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
    # Add tag if not in All Tasks
    if current_category_id == 0 and pref.get_tag():
        cat_id_of_current_task = task["category_id"]
        if cat_id_of_current_task != 0:
            text = "[" + cat.get_category_by_id(cat_id_of_current_task)["name"] +  "] " + text

    if len(text) > available_width:
        visible_text = text[:available_width]
    else:
        visible_text = text
        
    if task.get('status', False) and st.get_strikethrough() and not is_selected:
        strikethrough_desc = ""
        for char in visible_text:
            strikethrough_desc += (char + "\u0336")
        visible_text = strikethrough_desc
    
    # Display text at calculated position with proper styling
    if is_selected:
        stdscr.attron(curses.color_pair(clr.selection_color_pair_num))
        stdscr.addstr(row, total_indent, visible_text)
        # Fill remaining space with spaces
        for i in range(available_width - len(visible_text) + 1):
            stdscr.addstr(' ')
        stdscr.addstr(row, date_pos, date_str)
        stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))
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
            stdscr.attron(curses.color_pair(clr.selection_color_pair_num))
            stdscr.addstr(row, right_frame_pos - 1, ' ')
            stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))
        stdscr.addstr(row, right_frame_pos, '│')
    except curses.error:
        pass


def print_task_selected_with_offset(stdscr, task, row, x_offset=0, display_id=None, current_category_id=0):
    """Print a selected task with offset"""
    stdscr.attron(curses.color_pair(clr.selection_color_pair_num))
    print_task_with_offset(stdscr, task, row, True, x_offset, display_id, current_category_id)
    stdscr.attroff(curses.color_pair(clr.selection_color_pair_num))

def print_pref_panel(stdscr, current_selection_index=0):
    """
    Print the preference panel centered in the task area with ">" marker for selected preference
    and colored active options
    
    Args:
        stdscr: The curses window
        current_selection_index: Index of the currently selected preference (default: 0)
    """
    
    # Get preference panel content
    pref_content_lines = msg.pref_panel.strip().split("\n")

    # Calculate dimensions and position
    max_y, max_x = stdscr.getmaxyx()
    width = len(pref_content_lines[0])  # Use first line for width calculation
    available_width = max(0, max_x - 16)
    center_offset_x = max(0, (available_width - width) // 2) - 1
    center_offset_y = max(0, (max_y - len(pref_content_lines)) // 2) - 1
    
    clear_task_panel(stdscr, max_y)
    
    # Get current preference values for coloring
    tag_enabled = pref.get_tag()
    strikethrough_enabled = st.get_strikethrough()
    current_color = clr.get_color_selected_str()
    current_date_format = pref.get_date_format()
    autosort_flagged = pref.get_autosort_flagged()
    autosort_done = pref.get_autosort_done()
    
    # Format each line with ">" for selected item
    formatted_content = []
    for i, line in enumerate(pref_content_lines):
        if i == current_selection_index + 2:  # +2 because one pref every 2 lines
            formatted_content.append(f"  {line[0:2]}>{line[3:]}")
        else:
            formatted_content.append(f"  {line}")
    
    # Print each line of the panel with appropriate formatting
    for y in range(0, min(len(formatted_content), max_y - 2)):
        line = formatted_content[y]
        
        # Draw the top frame (first line)
        if y == 0:
            stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x, line)
            continue
            
        # Process and draw content lines
        if "Tag:" in line:
            value = "on" if tag_enabled else "off"
            pos = line.find(value)
            print_pref_line_on_off(stdscr, y, pos, line, center_offset_x, center_offset_y, value)
                
        elif "Strikethrough:" in line:
            value = "on" if strikethrough_enabled else "off"
            pos = line.find(value)
            print_pref_line_on_off(stdscr, y, pos, line, center_offset_x, center_offset_y, value)                
                
        elif "Color:" in line:
            pos = line.find(current_color)
            if pos > 0:
                # Print the first part (before the value)
                prefix = line[:pos]
                stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x, prefix)
                
                # Print the value with color-specific highlighting
                stdscr.attron(curses.color_pair(clr.get_current_color_pair_number()))
                stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x + pos, current_color)
                stdscr.attroff(curses.color_pair(clr.get_current_color_pair_number()))
                
                # Print the suffix (after the value)
                suffix = line[pos + len(current_color):]
                stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x + pos + len(current_color), suffix)
            else:
                # Fallback if value not found
                stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x, line)
                
        elif "Date format:" in line:
            pos = line.find(current_date_format)
            if pos > 0:
                # Print the first part (before the value)
                prefix = line[:pos]
                stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x, prefix)
                
                stdscr.attron(curses.color_pair(clr.get_current_color_pair_number()))
                stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x + pos, current_date_format)
                stdscr.attroff(curses.color_pair(clr.get_current_color_pair_number()))
                
                # Print the suffix (after the value)
                suffix = line[pos + len(current_date_format):]
                stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x + pos + len(current_date_format), suffix)
            else:
                # Fallback if value not found
                stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x, line)
        elif "Autosort flagged:" in line:
            value = "on" if autosort_flagged else "off"
            pos = line.find(value)
            print_pref_line_on_off(stdscr, y, pos, line, center_offset_x, center_offset_y, value)
        elif "Autosort done:" in line:
            value = "on" if autosort_done else "off"
            pos = line.rfind(value) # reverse find because done contains "on" as well
            print_pref_line_on_off(stdscr, y, pos, line, center_offset_x, center_offset_y, value)
        else:
            # Print other lines without special formatting
            stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x, line)
    
    print_right_frame(stdscr, max_y, max_x)
    print_q_to_close(stdscr, "preferences", max_x, max_y)
    
def print_pref_line_on_off(stdscr, y, pos, line, center_offset_x, center_offset_y, value):
    if pos > 0:
        # Print the first part (before the value)
        prefix = line[:pos]
        stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x, prefix)
        
        # Print the value with fixed color (green for "on", red for "off")
        if value == "on":
            green_pair_num = clr.get_color_pair_num_by_str("green")
            stdscr.attron(curses.color_pair(green_pair_num))
            stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x + pos, value)
            stdscr.attroff(curses.color_pair(green_pair_num))
        else:  # "off"
            red_pair_num = clr.get_color_pair_num_by_str("red")
            stdscr.attron(curses.color_pair(red_pair_num))
            stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x + pos, value)
            stdscr.attroff(curses.color_pair(red_pair_num))
        
        # Print the suffix (after the value)
        suffix = line[pos + len(value):]
        stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x + pos + len(value), suffix)
    else:
        # Fallback if value not found
        stdscr.addstr(y + center_offset_y + 1, 16 + center_offset_x, line)


def clear_task_panel(stdscr, max_y):
    for i in range(1, max_y - 1):
        try:
            stdscr.move(i, 16)
            stdscr.clrtoeol()
        except curses.error:
            continue
        
def print_q_to_close(stdscr, page, max_x, max_y):
    hint = f"┤Press 'q' to close {page}├"
    hint_pos_x = (max_x - 15) // 2 + 15 - len(hint) // 2
    stdscr.addstr(max_y - 1, hint_pos_x, hint)

# Functions for drawing frames and separators
def print_right_frame(stdscr, max_y, max_x):
    for y in range(1, max_y - 1):
        stdscr.addstr(y, max_x - 1, "│")

def print_left_frame(stdscr, max_y):
    for y in range(1, max_y - 1):
        stdscr.addstr(y, 0, '│')
        
def print_top_frame(stdscr, max_x):
    for x in range(1, max_x):
        stdscr.addstr(0, x, '─')

def print_bottom_frame(stdscr, max_y, max_x):
    for x in range(1, max_x):
        stdscr.addstr(max_y - 1, x, '─')

def print_top_right_corner(stdscr, max_x):
    stdscr.addstr(0, max_x - 1, "┐")

def print_top_left_corner(stdscr):
    stdscr.addstr(0, 0, "┌")
    
def print_bottom_right_corner(stdscr, max_x, max_y):
    stdscr.addstr(max_y - 1, max_x - 1, "┘")

def print_bottom_left_corner(stdscr, max_y):
    stdscr.addstr(max_y - 1, 0, "└")
    
def print_sidebar_task_panel_separator(stdscr, max_y):
    for y in range(1, max_y - 1):
        stdscr.addstr(y, 15, "│")

def print_seperator_connector_top(stdscr):
    stdscr.addstr(0, 15, "┬")

def print_seperator_connector_bottom(stdscr, max_y):
    stdscr.addstr(max_y - 1, 15, "┴")
    
def print_frame_all(stdscr):
    max_y, max_x = stdscr.getmaxyx()
    print_top_left_corner(stdscr)
    print_top_frame(stdscr, max_x)
    print_top_right_corner(stdscr, max_x)
    print_bottom_left_corner(stdscr, max_y)
    print_bottom_frame(stdscr, max_y, max_x)
    print_bottom_right_corner(stdscr, max_x, max_y)
    print_right_frame(stdscr, max_y, max_x)
    print_left_frame(stdscr, max_y)
    print_seperator_connector_top(stdscr)
    print_seperator_connector_bottom(stdscr, max_y)
    print_sidebar_task_panel_separator(stdscr, max_y)
