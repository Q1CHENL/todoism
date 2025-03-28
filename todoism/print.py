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
import todoism.due as due

view_mode = 0
add_mode  = 1
edit_mode = 2

def print_version():
    print("todoism v1.21.6")

def print_q_to_close(stdscr, page):
    hint = f"Press 'q' to close {page}"
    hint_pos_x = (st.latest_max_x - len(hint)) // 2 
    sf.safe_addstr(stdscr, st.latest_max_y - 2, hint_pos_x, hint, clr.get_bkg_color_pair())

def clear_all_except_outer_frames(stdscr):
    for y in range(1, st.latest_max_y - 1):
        sf.safe_addstr(stdscr, y, 1, ' ' * (st.latest_max_x - 2), clr.get_bkg_color_pair())

def clear_sidebar_area(stdscr):
    for y in range(1, st.latest_max_y - 3):
        sf.safe_addstr(stdscr, y, 1, ' ' * (cat.SIDEBAR_WIDTH - 2), clr.get_bkg_color_pair())

def clear_task_panel(stdscr):
    for y in range(1, st.latest_max_y - 3):    
        sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH, ' ' * (st.latest_max_x - cat.SIDEBAR_WIDTH - 1), clr.get_bkg_color_pair())

def clear_status(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 2, st.latest_max_x - 35, ' ' * 34, clr.get_bkg_color_pair())

def clear_bottom_bar_except_status(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 2, 1, ' ' * (st.latest_max_x - 37), clr.get_bkg_color_pair())
    
def clear_bottom_bar(stdscr):
    clear_status(stdscr)
    clear_bottom_bar_except_status(stdscr)
    
def print_github_page_line(stdscr, line):
    sf.safe_appendstr(stdscr, line[:line.find("Github page")])
    attr = clr.get_theme_color_pair_for_text() | curses.A_UNDERLINE
    sf.safe_appendstr(stdscr, "Github page", attr)
    sf.safe_appendstr(stdscr, line[line.find("Github page") + len("Github page"):])

def print_msg_in_task_panel(stdscr, msg, x_offset=cat.MAX_CATEGORY_NAME_LENGTH):
    """Print a message box with proper centering in the task area with optional highlighting"""

    clear_task_panel(stdscr)
    attr = curses.color_pair(clr.SELECTION_COLOR_PAIR_NUM) if not st.focus_manager.is_sidebar_focused() and not st.searching else 0
    print_msg(stdscr, msg, x_offset, attr)
    print_right_frame(stdscr)
    
def print_msg(stdscr, msg, x_offset=0, attr=0):
    """Print a message box with proper centering in the task area with optional highlighting"""
    
    lines = msg.split('\n')
    width = len(lines[1]) if len(lines) > 1 else len(lines[0])
    # Calculate available width for task area (total width minus sidebar)
    available_width = max(0, st.latest_max_x - x_offset)
    center_offset_x = max(0, (available_width - width) // 2)
    center_offset_y = max(0, (st.latest_max_y - len(lines)) // 2)
        
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
                    if line.find("Github page") > 0:
                        print_github_page_line(stdscr, line)
                    else:
                        sf.safe_appendstr(stdscr, line[:available_space], attr)
            else:
                if line.find("Github page") > 0:
                    print_github_page_line(stdscr, line)
                else:
                    sf.safe_appendstr(stdscr, line, attr)

def print_task_symbols(stdscr, task, y, is_selected=False):
    """Print task flag and status symbols with appropriate colors
    
    Args:
        stdscr: The curses window
        task: The task data dictionary
        y: The row position
        is_selected: Whether the task is selected
    """
    attr_bkg = curses.color_pair(clr.SELECTION_COLOR_PAIR_NUM)
    attr_space = attr_bkg if is_selected else 0
    attr_red = clr.get_color_pair_by_str("red")
    attr_green = clr.get_color_pair_by_str("green")
    
    if task.get("flagged", False):
        sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 3, '⚑', attr_bkg if is_selected else attr_red)
    else:
        sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 3, ' ', attr_space)
    # Add space between flag and status
    sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 3 + 1, ' ', attr_space)

    if task.get("status", False):
        sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 5, '✓', attr_bkg if is_selected else attr_green)
    else:
        sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 5, ' ', attr_space)
    sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH + 5 + 1, ' ', attr_space)
    
def print_editing_entry(stdscr, entry, text_key, y, is_selected=False, scroll_left=0, is_edit_mode=False):
    """Render a task with proper formatting and positioning"""
    
    if st.focus_manager.is_sidebar_focused():
        print_category(stdscr, entry, y, is_selected)
        return min(len(entry["name"]) + 2, 14)
    
    attr = curses.color_pair(clr.SELECTION_COLOR_PAIR_NUM)
    sf.safe_addstr(stdscr, y, cat.SIDEBAR_WIDTH, f"{entry['id']:2d} ", attr)
    print_task_symbols(stdscr, entry, y, is_selected=is_selected)
        
    due_str = due.get_due_str(entry)    
    due_pos = st.latest_max_x - len(due_str) - 1  # Account for right frame
    
    text_start_pos = cat.SIDEBAR_WIDTH + tsk.TASK_INDENT_IN_TASK_PANEL
    # Calculate available width for text
    available_width = due_pos - 2 - text_start_pos + 1
    
    # In view mode, we just show what fits; in edit mode, we scroll
    total_text_length = len(entry[text_key])
    
    # Calculate visible portion of text based on scroll offset
    visible_start_index = scroll_left
    visible_end_index = min(total_text_length, scroll_left + available_width - 1)
    visible_text = entry[text_key][visible_start_index:visible_end_index + 1]

    sf.safe_addstr(stdscr, y, text_start_pos, visible_text, curses.color_pair(clr.SELECTION_COLOR_PAIR_NUM))

    trailing_blank_space_num = available_width - len(visible_text) + 1    
    for _ in range(trailing_blank_space_num):
        sf.safe_appendstr(stdscr, ' ', curses.color_pair(clr.SELECTION_COLOR_PAIR_NUM))

    sf.safe_appendstr(stdscr, due_str, curses.color_pair(clr.SELECTION_COLOR_PAIR_NUM))
    sf.safe_appendstr(stdscr, ' ', curses.color_pair(clr.SELECTION_COLOR_PAIR_NUM))
    sf.safe_addstr(stdscr, y, st.latest_max_x - 1, '│')

def print_status_bar(stdscr):
    """Print centered status bar with progress, percentage, date and time"""
    done_cnt = tsk.done_count(st.filtered_tasks)
    
    # Calculate percentage
    percent_value = (done_cnt/st.task_cnt)*100 if st.task_cnt > 0 else 0
    percent_text = f"({percent_value:.0f}%)"
    
    color_text = "red" if percent_value < 33 else "yellow" if percent_value < 67 else "green"
    color_pair = clr.get_color_pair_by_str(color_text)
    
    # Add command hint at the beginning (dimmed)
    hint_text = ":help for info or '/' to search for tasks"
    sf.safe_addstr(stdscr, st.latest_max_y - 2, 1, hint_text, curses.A_DIM)
    
    # Split the status into parts for coloring
    status_prefix = f"Done: {done_cnt}/{st.task_cnt} "
    
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
    datetime_str = f"{date_str} {time_str}"
    
    start_pos = st.latest_max_x - 18 - len(datetime_str) - 2
    
    first_len = len(status_prefix + percent_text)
    padding = " " * (18 - first_len)
    sf.safe_addstr(stdscr, st.latest_max_y - 2, start_pos, status_prefix)
    sf.safe_appendstr(stdscr, percent_text, color_pair)
    sf.safe_appendstr(stdscr, padding)
    sf.safe_appendstr(stdscr, datetime_str)


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
    attr = 0
    if is_selected and st.focus_manager.is_sidebar_focused():
        attr = curses.color_pair(clr.SELECTION_COLOR_PAIR_NUM)
    elif is_selected and not st.focus_manager.is_sidebar_focused():
        attr = clr.get_theme_color_pair_for_text() | curses.A_BOLD
            
    sf.safe_addstr(stdscr, y, 1, ' ', attr)
    # Display name with fixed width - now at position 2 (after the left frame)
    sf.safe_addstr(stdscr, y, 2, category["name"], attr)
    # Fill remaining space with spaces to ensure fixed width
    padding = cat.MAX_CATEGORY_NAME_LENGTH + 1 - len(category["name"])
    if padding > 0:
        sf.safe_appendstr(stdscr, ' ' * padding, attr)

def print_task_entries(stdscr, x_offset=0):
    """Print tasks with horizontal offset to accommodate sidebar"""

    sidebar_focused = st.focus_manager.is_sidebar_focused()
    if st.filtered_tasks and st.start_task_id > 0:
        for i, task in enumerate(st.filtered_tasks[st.start_task_id - 1:st.end_task_id]):
            row = i + 1  # +1 due to status bar
            is_selected = st.start_task_id + i == st.current_task_id and not sidebar_focused and not st.adding_task 
            print_task_entry(stdscr, task, row, is_selected=is_selected, x_offset=x_offset)

def print_task_entry(stdscr, task, row, is_selected=False, x_offset=0):
    """Print a task with horizontal offset and optional display ID override"""
    
    print_task_symbols(stdscr, task, row, is_selected=is_selected)
    
    due_str = due.get_due_str(task)
    due_pos = st.latest_max_x - len(due_str) - 1  # Only 1 char gap from right frame
    
    # Calculate available space for text
    total_indent = x_offset + tsk.TASK_INDENT_IN_TASK_PANEL
    available_width = due_pos - total_indent # Space for gap before date
    
    # Handle text display
    text = task["description"]

    if (st.current_category_id == 0 or st.searching) and pref.get_tag():
        cat_id_of_current_task = task["category_id"]
        if cat_id_of_current_task != 0:
            text = "[" + cat.get_category_by_id(cat_id_of_current_task)["name"] +  "] " + text

    if len(text) > available_width:
        visible_text = text[:available_width - 1]
    else:
        visible_text = text
        
    is_done = task.get("status", False)
    if is_done and stk.get_strikethrough() and not is_selected:
        visible_text = stk.apply(visible_text)
        
    task_id = task["id"]
    attr = clr.get_theme_color_pair_for_selection()
    attr_done = curses.A_DIM
    
    if is_selected:
        sf.safe_addstr(stdscr, row, x_offset, f"{task_id:2d} ", attr)
        sf.safe_addstr(stdscr, row, total_indent, visible_text, attr)
        # Fill remaining space with spaces
        for _ in range(available_width - len(visible_text) + 1):
            sf.safe_appendstr(stdscr, ' ', attr)
        sf.safe_addstr(stdscr, row, due_pos, due_str, attr)
        sf.safe_addstr(stdscr, row, st.latest_max_x - 1, ' ', attr)
    else:
        attr_due = clr.get_theme_color_pair_for_text() if task["due"] != "" else 0
        sf.safe_addstr(stdscr, row, x_offset, f"{task_id:2d} ")
        sf.safe_addstr(stdscr, row, total_indent, visible_text, (attr_done if is_done else 0) | attr_due)
        sf.safe_addstr(stdscr, row, due_pos, due_str, (attr_done if is_done else 0) | attr_due)
        sf.safe_addstr(stdscr, row, st.latest_max_x - 1, '│')

def print_whole_view(stdscr, categories, category_start_index):
    """Print the complete UI with sidebar and task list"""
    
    clear_task_panel(stdscr)
    if st.task_cnt == 0:
        message = msg.EMPTY_MSG if not st.searching else msg.NO_TASKS_FOUND_MSG
        print_msg_in_task_panel(stdscr, message, cat.SIDEBAR_WIDTH)
    else:
        print_task_entries(stdscr, cat.SIDEBAR_WIDTH)
        
    clear_sidebar_area(stdscr)
    print_category_entries(stdscr, categories, category_start_index)
    print_frame_all(stdscr)
    clear_status(stdscr)
    print_status_bar(stdscr)

def print_pref_panel(stdscr, current_selection_index=0):
    """
    Print the preference panel centered in the task area with ">" marker for selected preference
    and colored active options
    
    Args:
        stdscr: The curses window
        current_selection_index: Index of the currently selected preference (default: 0)
    """
    
    # Get preference panel content
    pref_content_lines = msg.PREF_PANEL.strip().split("\n")

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
    sort_by_flagged = pref.get_sort_by_flagged()
    sort_by_done = pref.get_sort_by_done()
    
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
        if "Tag in All Tasks:" in line:
            value = "on" if tag_enabled else "off"
            pos = line.find(value)
            print_pref_line_on_off_adaptive(stdscr, y, pos, line, center_offset_x, center_offset_y, value)
                
        elif "Strikethrough:" in line:
            value = "on" if strikethrough_enabled else "off"
            pos = line.find(value)
            print_pref_line_on_off_adaptive(stdscr, y, pos, line, center_offset_x, center_offset_y, value)                
                
        elif "Theme:" in line and current_color in line:
            pos = line.find(current_color)
            print_pref_line_with_highlight(stdscr, y, pos, line, center_offset_x, center_offset_y, 
                                         current_color, clr.get_theme_color_pair_for_text())
                
        elif "Date format:" in line and current_date_format in line:
            pos = line.find(current_date_format)
            print_pref_line_with_highlight(stdscr, y, pos, line, center_offset_x, center_offset_y, 
                                         current_date_format, clr.get_theme_color_pair_for_text())
            
        elif "Sort by flagged:" in line:
            value = "on" if sort_by_flagged else "off"
            pos = line.find(value)
            print_pref_line_on_off_adaptive(stdscr, y, pos, line, center_offset_x, center_offset_y, value)
            
        elif "Sort by done:" in line:
            value = "on" if sort_by_done else "off"
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
        
    if value == "on":
        attr = clr.get_color_pair_by_str("green")
        sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x + pos, value[:st.latest_max_x-(center_offset_x+pos)-1], attr)
    else:  # "off"
        attr = clr.get_color_pair_by_str("red")
        sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x + pos, value[:st.latest_max_x-(center_offset_x+pos)-1], attr)
    
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
    sf.safe_addstr(stdscr, y + center_offset_y + 1, center_offset_x + pos, value[:st.latest_max_x-(center_offset_x+pos)-1], color_pair)
    
    # Print the suffix (part after the value) if it fits
    suffix = line[pos + len(value):]
    suffix_pos = center_offset_x + pos + len(value)
    if suffix_pos < st.latest_max_x and len(suffix) > 0:
        sf.safe_addstr(stdscr, y + center_offset_y + 1, suffix_pos, suffix[:st.latest_max_x-suffix_pos-1])

def print_all_cli(todos):
    if len(todos) == 0:
        print("no todos yet")
        exit(0)
        
    tsk.reassign_task_ids(todos)
    done_fmt = "\033[9m%s\033[0m"     # strikethrough
    flag_color = "\033[31m%s\033[0m"   # red for flag
    check_color = "\033[32m%s\033[0m"  # green for checkmark
    
    for todo in todos:
        id_part = f'#{todo["id"]:02d}'

        flag_symbol = flag_color % "⚑ " if todo.get("flagged") else "  "
        check_symbol = check_color % "✓ " if todo.get("status") else "  "
        
        description = todo["description"]
        if todo.get("status"):
            description = done_fmt % description
            
        todo_line = f'{id_part} {flag_symbol}{check_symbol}{description} ({todo["due"]})'
        print(todo_line)
        
# Functions for drawing frames and separators
def print_right_frame(stdscr):
    for y in range(1, st.latest_max_y - 3):
        sf.safe_addstr(stdscr, y, st.latest_max_x - 1, "│")

def print_right_frame_2nd(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 2, st.latest_max_x - 1, "│")

def print_left_frame(stdscr):
    for y in range(1, st.latest_max_y - 3):
        sf.safe_addstr(stdscr, y, 0, '│')
        
def print_left_frame_2nd(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 2, 0, "│")
        
def print_top_frame(stdscr):
    for x in range(1, st.latest_max_x - 1):
        sf.safe_addstr(stdscr, 0, x, '─')

def print_bottom_frame(stdscr):    
    for x in range(1, st.latest_max_x - 2):
        sf.safe_addstr(stdscr, st.latest_max_y - 1, x, '─')
    
def print_2nd_bottom(stdscr):
    for x in range(1, st.latest_max_x - 1):
        sf.safe_addstr(stdscr, st.latest_max_y - 3, x, '─')
        
def print_2nd_bottom_connector_up(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 3, 15, "┴")

def print_2nd_bottom_connector_left(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 3, 0, "├")

def print_2nd_bottom_right_corner(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 3, st.latest_max_x - 1, "┤")

def print_top_right_corner(stdscr):
    sf.safe_addstr(stdscr, 0, st.latest_max_x - 1, "┐")

def print_top_left_corner(stdscr):
    sf.safe_addstr(stdscr, 0, 0, "┌")
    
def print_bottom_right_corner(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "┘")
    sf.safe_insstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "─")

def print_bottom_left_corner(stdscr):
    sf.safe_addstr(stdscr, st.latest_max_y - 1, 0, "└")
    
def print_sidebar_task_panel_separator(stdscr):
    for y in range(1, st.latest_max_y - 3):
        sf.safe_addstr(stdscr, y, 15, "│")

def print_separator_connector_top(stdscr):
    sf.safe_addstr(stdscr, 0, 15, "┬")

def print_frame_all(stdscr):
    print_top_left_corner(stdscr)
    print_bottom_left_corner(stdscr)
    print_left_frame(stdscr)
    print_left_frame_2nd(stdscr)
    print_top_right_corner(stdscr)
    print_top_frame(stdscr)
    print_right_frame(stdscr)
    print_bottom_frame(stdscr)
    print_2nd_bottom(stdscr)
    print_2nd_bottom_connector_up(stdscr)
    print_2nd_bottom_connector_left(stdscr)
    print_separator_connector_top(stdscr)
    print_2nd_bottom_right_corner(stdscr)
    print_right_frame_2nd(stdscr)
    print_sidebar_task_panel_separator(stdscr)
    # Trick for last char (bottom right) error in cursor window    
    sf.safe_addstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "┘")
    sf.safe_insstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "─")

def print_outer_frame(stdscr):
    print_top_left_corner(stdscr)
    print_bottom_left_corner(stdscr)
    print_left_frame(stdscr)
    sf.safe_addstr(stdscr, st.latest_max_y - 3, 0, "│")
    print_left_frame_2nd(stdscr)
    print_top_right_corner(stdscr)
    print_top_frame(stdscr)
    print_right_frame(stdscr)
    print_right_frame_2nd(stdscr)
    sf.safe_addstr(stdscr, st.latest_max_y - 3, st.latest_max_x - 1, "│")
    print_bottom_frame(stdscr)
    # Trick for last char (bottom right) error in cursor window
    sf.safe_addstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "┘")
    sf.safe_insstr(stdscr, st.latest_max_y - 1, st.latest_max_x - 2, "─")
