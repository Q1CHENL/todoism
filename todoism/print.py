import curses
from datetime import datetime
import todoism.strikethrough as stk
import todoism.message as msg
import todoism.color as clr
import todoism.category as cat
import todoism.preference as pref
import todoism.state as st
import todoism.task as tsk
import todoism.safe as sf

view_mode = 0
add_mode  = 1
edit_mode = 2

def print_msg_center(stdscr, message, color_pair=0, highlight_line=-1):    
    lines = message.strip().split("\n")
    start_y = max(0, (st.latest_max_y - len(lines)) // 2)
    
    for i, line in enumerate(lines):
        if line.strip():  # Only print non-empty lines
            start_x = max(0, (st.latest_max_x - len(line)) // 2)
            if i == highlight_line and color_pair > 0:
                stdscr.attron(curses.color_pair(color_pair))
                sf.safe_addstr(stdscr, start_y + i, start_x, line)
                stdscr.attroff(curses.color_pair(color_pair))
            else:
                sf.safe_addstr(stdscr, start_y + i, start_x, line)
    
    stdscr.refresh()

def print_msg_in_task_panel(stdscr, msg, x_offset=cat.MAX_CATEGORY_NAME_LENGTH, highlight=False):
    """Print a message box with proper centering in the task area with optional highlighting"""
    lines = msg.split('\n')
    width = len(lines[1])

    # Ensure we have minimum required space
    if st.latest_max_y < 2 or st.latest_max_x < x_offset + 1:
        return
    
    # Calculate available width for task area (total width minus sidebar)
    available_width = max(0, st.latest_max_x - x_offset)
    
    # Calculate center position within the available task area
    # Ensure center_offset is never negative
    center_offset_x = max(0, (available_width - width) // 2)
    center_offset_y = max(0, (st.latest_max_y - len(lines)) // 2)
    
    clear_task_panel(stdscr)
    
    if highlight:
        stdscr.attron(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
    
    # Print each line separately at the calculated position
    for i, line in enumerate(lines):
        y = i + 1  # Start at row 1 (row 0 is status bar)
        if y < st.latest_max_y - 1 and line.strip():  # Only print non-empty lines and check bounds
            # Position cursor at sidebar edge + centering offset
            sf.safe_move(stdscr, y + center_offset_y, x_offset + center_offset_x)
            # Print the line directly, truncating if necessary
            if x_offset + center_offset_x + len(line) > st.latest_max_x:
                # Truncate line to fit available space
                available_space = st.latest_max_x - (x_offset + center_offset_x)
                if available_space > 0:
                    sf.safe_appendstr(stdscr, line[:available_space])
            else:
                sf.safe_appendstr(stdscr, line)

    if highlight:
        stdscr.attroff(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
    
    # Draw the right frame for each line
    print_right_frame(stdscr)
    
def print_msg(stdscr, msg, x_offset=0, y_offset=0, highlight=False):
    """Print a message box with proper centering in the task area with optional highlighting"""
    lines = msg.split('\n')
    width = len(lines[1])
    
    # Ensure we have minimum required space
    if st.latest_max_y < 2 or st.latest_max_x < x_offset + 1:
        return
    
    # Calculate available width for task area (total width minus sidebar)
    available_width = max(0, st.latest_max_x - x_offset)
    center_offset_x = max(0, (available_width - width) // 2)
    center_offset_y = max(0, (st.latest_max_y - len(lines)) // 2)
    
    # Apply highlighting if requested
    if highlight:
        stdscr.attron(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
    
    # Print each line separately at the calculated position
    for i, line in enumerate(lines):
        y = i + 1  # Start at row 1 (row 0 is status bar)
        if y < st.latest_max_y - 1 and line.strip():  # Only print non-empty lines and check bounds
            # Position cursor at sidebar edge + centering offset
            sf.safe_move(stdscr, y + center_offset_y, x_offset + center_offset_x)
            # Print the line directly, truncating if necessary
            if x_offset + center_offset_x + len(line) > st.latest_max_x:
                # Truncate line to fit available space
                available_space = st.latest_max_x - (x_offset + center_offset_x)
                if available_space > 0:
                    sf.safe_addstr(stdscr, line[:available_space])
            else:
                sf.safe_appendstr(stdscr, line)
            
    # Remove highlighting if it was applied
    if highlight:
        stdscr.attroff(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))

    stdscr.noutrefresh()
    curses.doupdate()

def print_version():
    print("todoism v1.21.4")

def print_task_symbols(stdscr, task, y, is_selected=False):
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
    if task.get("flagged", False):
        if not is_selected:
            flag_color = clr.get_color_pair_num_by_str_text("red")
            stdscr.attron(curses.color_pair(flag_color))
            sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 3, '⚑')
            stdscr.attroff(curses.color_pair(flag_color))
        else:
            sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 3, '⚑')
    else:
        sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 3, ' ')
    
    # Add space between flag and status
    sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 3 + 1, ' ')
    
    # Print status indicator second
    if task.get("status", False):
        if not is_selected:
            check_color = clr.get_color_pair_num_by_str_text("green")
            stdscr.attron(curses.color_pair(check_color))
            sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 5, '✓')
            stdscr.attroff(curses.color_pair(check_color))
        else:
            sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 5, '✓')
    else:
        sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 5, ' ')
    
    sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 5 + 1, ' ')
    
def print_editing_category(stdscr, category, y, is_selected=False):
    sf.safe_addstr(stdscr, y, 0, "│")
    print_category(stdscr, category, y, is_selected)
    
def print_editing_entry(stdscr, task, text_key, y, is_selected=False, scroll_left=0, is_edit_mode=False):
    """Render a task with proper formatting and positioning"""
    
    if st.focus_manager.is_sidebar_focused():
        print_editing_category(stdscr, task, y, is_selected)
        return min(len(task["name"]) + 2, 14)
    
    # Clear the row for custom rendering
    sf.safe_move(stdscr, y, cat.SIDEBAR_WIDTH)
    stdscr.clrtoeol()
    
    sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH, f"{task["id"]:2d} ")
    print_task_symbols(stdscr, task, y, is_selected=is_selected)
    
    # Calculate date position and available text space
    date_str = task["date"]
    date_padding = 1  # Space between description and date
    date_pos = st.latest_max_x - len(date_str) - date_padding - 1  # Account for right frame
    
    text_start_pos = cat.SIDEBAR_WIDTH + tsk.TASK_INDENT_IN_TASK_PANEL  # Combined offset    
    # Calculate available width for text
    available_width = date_pos - text_start_pos - 1
    
    # In view mode, we just show what fits; in edit mode, we scroll
    total_text_length = len(task[text_key])
    
    # Calculate visible portion of text based on scroll offset
    visible_start = scroll_left
    visible_end = min(total_text_length, scroll_left + available_width)
    visible_text = task[text_key][visible_start:visible_end]

    highlight_trailing_blank_space = 0
    # Display text at calculated position
    if task.get("status", False) and not is_selected and not is_edit_mode:
        stdscr.attron(curses.A_DIM)
    sf.safe_addstr(stdscr, y, text_start_pos, visible_text)
    stdscr.attroff(curses.A_DIM)
    highlight_trailing_blank_space = available_width - len(visible_text) + 1    
    for i in range(highlight_trailing_blank_space):
        sf.safe_appendstr(stdscr, ' ')

    sf.safe_addstr(stdscr, y, date_pos, date_str)
    if is_selected:
        sf.safe_addstr(stdscr, y, date_pos + len(date_str), ' ')
    stdscr.attroff(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
    sf.safe_addstr(stdscr, y, st.latest_max_x - 1, '│')

    if is_selected:
        stdscr.attron(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))

def print_status_bar(stdscr):
    """Print centered status bar with progress, percentage, date and time"""

    # Reset all attributes at the start
    stdscr.attroff(curses.A_BOLD | curses.A_DIM | curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM) | 
                   curses.color_pair(2) | curses.color_pair(3) | curses.color_pair(4))
    
    # Calculate percentage
    percent_value = (st.done_cnt/st.task_cnt)*100 if st.task_cnt > 0 else 0
    percent_text = f"({percent_value:.0f}%)"
    
    # Choose color based on percentage range
    if percent_value < 33:
        color_pair = clr.get_color_pair_num_by_str_text("red")
    elif percent_value < 67:
        color_pair = clr.get_color_pair_num_by_str_text("yellow")
    else:
        color_pair = clr.get_color_pair_num_by_str_text("green")
    
    # Split the status into parts for coloring
    status_prefix = f"┤Done: {st.done_cnt}/{st.task_cnt} "
    
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
    start_pos = (st.latest_max_x - total_len - cat.SIDEBAR_WIDTH) // 2 + cat.SIDEBAR_WIDTH
    
    # Clear only the top line
    sf.safe_move(stdscr, 0, 0)
    stdscr.clrtoeol()

    print_top_left_corner(stdscr)
    print_top_frame(stdscr)
    print_separator_connector_top(stdscr)
    print_top_right_corner(stdscr)
    
    # Print centered status with colored percentage and datetime
    sf.safe_addstr(stdscr, 0, start_pos, status_prefix)
    stdscr.attron(curses.color_pair(color_pair))
    sf.safe_addstr(stdscr, 0, start_pos + len(status_prefix), percent_text)
    stdscr.attroff(curses.color_pair(color_pair))
    sf.safe_addstr(stdscr, 0, start_pos + len(status_prefix) + len(percent_text) + 2, datetime_str)
    
    # Ensure all attributes are reset at the end
    stdscr.attroff(curses.A_BOLD | curses.A_DIM | curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM) | 
                   curses.color_pair(2) | curses.color_pair(3) | curses.color_pair(4))

def print_all_cli(todos):
    if len(todos) == 0:
        print("no todos yet")
        exit(0)
        
    tsk.reassign_task_ids(todos)
    done_fmt = "\033[9m%s\033[0m"     # strikethrough
    flag_color = "\033[31m%s\033[0m"   # red for flag
    check_color = "\033[32m%s\033[0m"  # green for checkmark
    
    for todo in todos:
        id_part = f"#{todo["id"]:02d}"

        flag_symbol = flag_color % "⚑ " if todo.get("flagged") else "  "
        check_symbol = check_color % "✓ " if todo.get("status") else "  "
        
        description = todo["description"]
        if todo.get("status"):
            description = done_fmt % description
            
        todo_line = f"{id_part} {flag_symbol}{check_symbol}{description} ({todo["date"]})"
        print(todo_line)

def print_category_entries(stdscr, categories, start_index):
    """Print the category sidebar"""
    
    # Print visible categories
    visible_categories = categories[start_index:start_index + st.latest_max_capacity]
    for i, category in enumerate(visible_categories):
        row = i + 1  # Start from row 1 (row 0 is for status bar)
        is_selected = category["id"] == st.current_category_id
        print_category(stdscr, category, row, is_selected)

def print_category(stdscr, category, y, is_selected=False):
    """Print a single category in the sidebar with fixed width"""
    # Set format based on selection and focus
    if is_selected and st.focus_manager.is_sidebar_focused():
        stdscr.attron(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))  # Use the same highlight as tasks
    elif not st.focus_manager.is_sidebar_focused():
        if is_selected:
            stdscr.attron(curses.color_pair(clr.get_theme_color_pair_num_text()))
            stdscr.attron(curses.A_BOLD)
        else: 
            turnoff_all_attributes(stdscr)
            
    sf.safe_addstr(stdscr, y, 1, ' ')
    # Display name with fixed width - now at position 2 (after the left frame)
    sf.safe_addstr(stdscr, y, 2, category["name"])
    # Fill remaining space with spaces to ensure fixed width
    padding = cat.MAX_CATEGORY_NAME_LENGTH + 1 - len(category["name"])
    if padding > 0:
        sf.safe_appendstr(stdscr, ' ' * padding)

    # Reset attributes
    if is_selected and st.focus_manager.is_sidebar_focused():
        stdscr.attroff(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
    elif is_selected and not st.focus_manager.is_sidebar_focused():
        stdscr.attroff(curses.color_pair(clr.get_theme_color_pair_num_text()))
        stdscr.attroff(curses.A_BOLD)

def print_whole_view(stdscr, categories, category_start_index):
    """Print the complete UI with sidebar and task list"""
    # Get max visible height
    st.latest_max_y, _ = stdscr.getmaxyx()
    # Reduce max_height by 1 to account for bottom frame
    max_height = st.latest_max_y - 2  # -1 for status bar, -1 for bottom frame
    
    print_frame_all(stdscr)
    # Print status bar first
    print_status_bar(stdscr)
    
    # Clear sidebar area
    for y in range(1, max_height + 1):
        sf.safe_move(stdscr, y, 0)
        stdscr.clrtoeol()
    # Print visible categories
    visible_categories = categories[category_start_index:category_start_index + max_height]
    
    for i, category in enumerate(visible_categories):
        row = i + 1  # Start from row 1 (row 0 is for status bar)
        is_selected = category["id"] == st.current_category_id
        print_category(stdscr, category, row, is_selected)
    print_left_frame(stdscr)
    print_sidebar_task_panel_separator(stdscr)
    
    # Print tasks or empty message
    if st.task_cnt == 0:
        clear_task_panel(stdscr)
        # Print empty message with highlighting when task area has focus
        print_msg_in_task_panel(stdscr, msg.empty_msg, cat.SIDEBAR_WIDTH, highlight=False)
        print_right_frame(stdscr)
    else:
        print_task_entries(stdscr, cat.SIDEBAR_WIDTH)

    stdscr.noutrefresh()
    curses.doupdate()

def print_task_entries(stdscr, x_offset=0):
    """Print tasks with horizontal offset to accommodate sidebar"""

    clear_task_panel(stdscr)

    # Only print if we have tasks and a valid start index
    if st.filtered_tasks and st.start_task_id > 0:
        for i, task in enumerate(st.filtered_tasks[st.start_task_id - 1:st.end_task_id]):
            row = i + 1  # +1 due to status bar
            display_id = i + st.start_task_id  # Sequential display ID (1, 2, 3, etc.)
            
            if st.start_task_id + i == st.current_task_id and not st.focus_manager.is_sidebar_focused() and not st.adding_task:
                # Selected task
                print_task_entry_selected(stdscr, task, row, x_offset, display_id)
            else:
                # Normal task
                print_task_entry(stdscr, task, row, False, x_offset, display_id)
    

    # Print right frame of area without task entries, compensate for clearing the whole task panel
    # Might get error when resizing window while typing search query
    for y in range(len(st.filtered_tasks) if len(st.filtered_tasks) > 0 else 1, st.latest_max_y - 1):
        sf.safe_addstr(stdscr, y, st.latest_max_x - 1, "│")


    # Reset all attributes before drawing bottom right corner
    stdscr.attroff(curses.A_BOLD | curses.A_DIM | curses.A_REVERSE | curses.A_BLINK | 
                  curses.A_UNDERLINE | curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))

def print_task_entry(stdscr, task, row, is_selected, x_offset=0, display_id=None):
    """Print a task with horizontal offset and optional display ID override"""

    # Use display_id if provided, otherwise use task's actual ID
    id_to_show = display_id if display_id is not None else task["id"]
    
    if not is_selected:
        stdscr.attroff(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))

    # Print task ID
    sf.safe_addstr(stdscr, row, x_offset, f"{id_to_show:2d} ")
    
    # Print task symbols with swapped positions
    print_task_symbols(stdscr, task, row, is_selected=is_selected)
    
    # Calculate positions with right frame
    right_frame_pos = st.latest_max_x - 1
    date_str = task["date"]
    date_pos = right_frame_pos - len(date_str) - 1  # Only 1 char gap from right frame
    
    # Calculate available space for text
    total_indent = x_offset + tsk.TASK_INDENT_IN_TASK_PANEL
    available_width = date_pos - total_indent - 1  # Space for gap before date
    
    # Handle text display
    text = task["description"]

    if (st.current_category_id == 0 or st.searching) and pref.get_tag():
        cat_id_of_current_task = task["category_id"]
        if cat_id_of_current_task != 0:
            text = "[" + cat.get_category_by_id(cat_id_of_current_task)["name"] +  "] " + text

    if len(text) > available_width:
        visible_text = text[:available_width]
    else:
        visible_text = text
        
    if task.get("status", False) and stk.get_strikethrough() and not is_selected:
        visible_text = stk.apply(visible_text)
    
    if is_selected:
        stdscr.attron(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
        sf.safe_addstr(stdscr, row, total_indent, visible_text)
        # Fill remaining space with spaces
        for i in range(available_width - len(visible_text) + 1):
            sf.safe_appendstr(stdscr, ' ')
        sf.safe_addstr(stdscr, row, date_pos, date_str)
        stdscr.attroff(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
    else:
        if task.get("status", False):
            stdscr.attron(curses.A_DIM)
        sf.safe_addstr(stdscr, row, total_indent, visible_text)
        # Fill remaining space with spaces
        for i in range(available_width - len(visible_text)):
            sf.safe_appendstr(stdscr, ' ')
        # Print date
        sf.safe_addstr(stdscr, row, date_pos, date_str)
        if task.get("status", False):
            stdscr.attroff(curses.A_DIM)


    if is_selected:
        stdscr.attron(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
        sf.safe_addstr(stdscr, row, right_frame_pos - 1, ' ')
        stdscr.attroff(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
    sf.safe_addstr(stdscr, row, right_frame_pos, '│')


def print_task_entry_selected(stdscr, task, row, x_offset=0, display_id=None):
    """Print a selected task with offset"""
    stdscr.attron(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))
    print_task_entry(stdscr, task, row, True, x_offset, display_id)
    stdscr.attroff(curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM))

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

    # Calculate available width - adapt to screen size
    original_width = len(pref_content_lines[0]) if pref_content_lines else 0
    # Make sure panel is at least 20 chars wide or as wide as possible
    available_width = min(original_width, max(20, st.latest_max_x - 4))
    
    # Calculate center offsets (similar to print_msg)
    center_offset_x = max(0, (st.latest_max_x - available_width) // 2)
    center_offset_y = max(0, (st.latest_max_y - len(pref_content_lines)) // 2) - 1
    
    # Get current preference values for coloring
    tag_enabled = pref.get_tag()
    strikethrough_enabled = stk.get_strikethrough()
    current_color = clr.get_theme_color_str()
    current_date_format = pref.get_date_format()
    sort_flagged = pref.get_sort_flagged()
    sort_done = pref.get_sort_done()
    
    # Format each line with ">" for selected item
    # Adapt line width to available space
    formatted_content = []
    for i, line in enumerate(pref_content_lines):
        # Truncate line if needed
        if len(line) > available_width:
            line = line[:available_width]
            
        if i == current_selection_index + 2:  # one pref every 2 lines
            # Handle selection marker
            if len(line) >= 3:
                formatted_content.append(f"{line[0:2]}>{line[3:]}")
            else:
                formatted_content.append(line)
        else:
            formatted_content.append(line)
    
    # Print each line of the panel with appropriate formatting
    for y in range(0, min(len(formatted_content), st.latest_max_y - 2)):

        line = formatted_content[y]
        
        # Draw the top frame (first line)
        if y == 0:
            sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x, line[:st.latest_max_x-center_offset_x-1])
            continue
        
        # Process and draw content lines
        if "Tag:" in line:
            value = "on" if tag_enabled else "off"
            pos = line.find(value)
            print_pref_line_on_off_adaptive(stdscr, y, pos, line, center_offset_x, center_offset_y, value)
                
        elif "Strikethrough:" in line:
            value = "on" if strikethrough_enabled else "off"
            pos = line.find(value)
            print_pref_line_on_off_adaptive(stdscr, y, pos, line, center_offset_x, center_offset_y, value)                
                
        elif "Color:" in line and current_color in line:
            pos = line.find(current_color)
            print_pref_line_with_highlight(stdscr, y, pos, line, center_offset_x, center_offset_y, 
                                         current_color, clr.get_theme_color_pair_num_text())
                
        elif "Date format:" in line and current_date_format in line:
            pos = line.find(current_date_format)
            print_pref_line_with_highlight(stdscr, y, pos, line, center_offset_x, center_offset_y, 
                                         current_date_format, clr.get_theme_color_pair_num_text())
            
        elif "Sort by flagged:" in line:
            value = "on" if sort_flagged else "off"
            pos = line.find(value)
            print_pref_line_on_off_adaptive(stdscr, y, pos, line, center_offset_x, center_offset_y, value)
            
        elif "Sort by done:" in line:
            value = "on" if sort_done else "off"
            pos = line.rfind(value)  # reverse find because done contains "on" as well
            print_pref_line_on_off_adaptive(stdscr, y, pos, line, center_offset_x, center_offset_y, value)
            
        else:
            # Print other lines without special formatting
            sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x, line[:st.latest_max_x-center_offset_x-1])


def print_pref_line_on_off_adaptive(stdscr, y, pos, line, center_offset_x, center_offset_y, value):
    """Safely print a preference line with on/off value highlighted"""

    if pos <= 0:
        # Value not found, print the whole line
        sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x, line[:st.latest_max_x-center_offset_x-1])
        return
        
    # Print the prefix (part before the value)
    prefix = line[:pos]
    if center_offset_x + len(prefix) < st.latest_max_x:
        sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x, prefix[:st.latest_max_x-center_offset_x-1])
    
    # Determine if there's space for the value
    if center_offset_x + pos + len(value) > st.latest_max_x:
        return
        
    # Print the value with appropriate color
    if value == "on":
        green_pair_num = clr.get_color_pair_num_by_str_text("green")
        stdscr.attron(curses.color_pair(green_pair_num))
        sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x + pos, value[:st.latest_max_x-(center_offset_x+pos)-1])
        stdscr.attroff(curses.color_pair(green_pair_num))
    else:  # "off"
        red_pair_num = clr.get_color_pair_num_by_str_text("red")
        stdscr.attron(curses.color_pair(red_pair_num))
        sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x + pos, value[:st.latest_max_x-(center_offset_x+pos)-1])
        stdscr.attroff(curses.color_pair(red_pair_num))
    
    # Print the suffix (part after the value) if it fits
    suffix = line[pos + len(value):]
    suffix_pos = center_offset_x + pos + len(value)
    if suffix_pos < st.latest_max_x and len(suffix) > 0:
        sf.safe_addstr(stdscr, y + center_offset_y + 1, suffix_pos, suffix[:st.latest_max_x-suffix_pos-1])
        
def print_pref_line_with_highlight(stdscr, y, pos, line, center_offset_x, center_offset_y, value, color_pair):
    """Safely print a preference line with a highlighted value using specified color pair"""

    if pos <= 0:
        # Value not found, print the whole line
        sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x, line[:st.latest_max_x-center_offset_x-1])
        return
        
    # Print the prefix (part before the value)
    prefix = line[:pos]
    if center_offset_x + len(prefix) < st.latest_max_x:
        sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x, prefix[:st.latest_max_x-center_offset_x-1])
    
    # Determine if there's space for the value
    if center_offset_x + pos + len(value) > st.latest_max_x:
        return
        
    # Print the value with specified color
    stdscr.attron(curses.color_pair(color_pair))
    sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x + pos, value[:st.latest_max_x-(center_offset_x+pos)-1])
    stdscr.attroff(curses.color_pair(color_pair))
    
    # Print the suffix (part after the value) if it fits
    suffix = line[pos + len(value):]
    suffix_pos = center_offset_x + pos + len(value)
    if suffix_pos < st.latest_max_x and len(suffix) > 0:
        sf.safe_addstr(stdscr, y + center_offset_y + 1, suffix_pos, suffix[:st.latest_max_x-suffix_pos-1])

def clear_task_panel(stdscr):
    for i in range(1, st.latest_max_y - 1):    
        sf.safe_move(stdscr, i, cat.SIDEBAR_WIDTH)
        stdscr.clrtoeol()
        
def clear_inner_content(stdscr):
    # Clear all content exepct the outer frame
    for i in range(1, st.latest_max_y - 1):
        sf.safe_move(stdscr, i, 1)
        stdscr.clrtoeol()
        
def print_q_to_close(stdscr, page):
    hint = f"┤Press 'q' to close {page}├"
    hint_pos_x = (st.latest_max_x - len(hint)) // 2 
    sf.safe_addstr(stdscr, st.latest_max_y - 1, hint_pos_x, hint)

# Functions for drawing frames and separators
def print_right_frame(stdscr):
    for y in range(1, st.latest_max_y - 1):
        sf.safe_addstr(stdscr, y, st.latest_max_x - 1, "│")

def print_left_frame(stdscr):
    for y in range(1, st.latest_max_y - 1):
        sf.safe_addstr(stdscr, y, 0, '│')
        
def print_top_frame(stdscr):
    for x in range(1, st.latest_max_x - 1):
        sf.safe_addstr(stdscr, 0, x, '─')

def print_bottom_frame(stdscr):    
    for x in range(1, st.latest_max_x - 2):
        sf.safe_addstr(stdscr, st.latest_max_y - 1, x, '─')

def print_top_right_corner(stdscr):
    sf.safe_addstr(stdscr, 0, st.latest_max_x - 1, "┐")

def print_top_left_corner(stdscr):
    sf.safe_addstr(stdscr, 0, 0, "┌")
    
def print_bottom_right_corner(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "┘")
    sf.safe_insstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "─")

def print_bottom_left_corner(stdscr):
    # Reset attributes before drawing corner to prevent highlighting
    sf.safe_addstr(stdscr, st.latest_max_y - 1, 0, "└")
    
def print_sidebar_task_panel_separator(stdscr):
    for y in range(1, st.latest_max_y - 1):
        sf.safe_addstr(stdscr, y, 15, "│")

def print_separator_connector_top(stdscr):
    sf.safe_addstr(stdscr, 0, 15, "┬")

def print_separator_connector_bottom(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 1, 15, "┴")
    
def print_frame_all(stdscr):
    turnoff_all_attributes(stdscr)
    print_top_left_corner(stdscr)
    print_bottom_left_corner(stdscr)
    print_left_frame(stdscr)
    print_top_right_corner(stdscr)
    print_top_frame(stdscr)
    print_right_frame(stdscr)
    print_bottom_frame(stdscr)
    print_separator_connector_top(stdscr)
    print_separator_connector_bottom(stdscr)
    print_sidebar_task_panel_separator(stdscr)
    # Trick for last char (bottom right) error in cursor window    
    sf.safe_addstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "┘")
    sf.safe_insstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "─")

def print_outer_frame(stdscr):
    turnoff_all_attributes(stdscr)
    print_top_left_corner(stdscr)
    print_bottom_left_corner(stdscr)
    print_left_frame(stdscr)
    print_top_right_corner(stdscr)
    print_top_frame(stdscr)
    print_right_frame(stdscr)
    print_bottom_frame(stdscr)
    # Trick for last char (bottom right) error in cursor window
    sf.safe_addstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "┘")
    sf.safe_insstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "─")

def turnoff_all_attributes(stdscr):
    stdscr.attroff(curses.A_BOLD | curses.A_DIM | curses.A_REVERSE | curses.A_BLINK | 
                  curses.A_UNDERLINE | curses.color_pair(clr.BACKGROUND_COLOR_PAIR_NUM) |
                  curses.color_pair(clr.get_theme_color_pair_num_text()))