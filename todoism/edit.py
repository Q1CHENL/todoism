import curses
import todoism.print as pr
import todoism.task as tsk
import todoism.keycode as kc
import todoism.state as st
import todoism.category as cat
import todoism.safe as sf
import todoism.navigate as nv

def move_by_word(text, current_pos, direction):
    """Move cursor by word in the specified direction
    
    Args:
        text: The text string to navigate
        current_pos: Current cursor position in the text
        direction: -1 for left, 1 for right
        
    Returns:
        New cursor position
    """
    if direction < 0:  # Left
        # If at beginning or first position, can't go left
        if current_pos <= 0:
            return 0
            
        # Skip spaces going left
        pos = current_pos - 1
        while pos > 0 and text[pos].isspace():
            pos -= 1
            
        # Find start of word
        while pos > 0 and not text[pos-1].isspace():
            pos -= 1
            
        return pos
    else:  # Right
        # If at or beyond end, can't go right
        if current_pos >= len(text):
            return len(text)
            
        # Skip current word
        pos = current_pos
        while pos < len(text) and not text[pos].isspace():
            pos += 1
            
        # Skip spaces
        while pos < len(text) and text[pos].isspace():
            pos += 1
            
        return pos

def highlight_selection(stdscr, task, text_key, y, selection_start_idx_in_text, selection_end_idx_in_text, scroll_offset, max_visible_width):
    """
    Highlight the selected region of text in the task description.
    scroll_offset: length of text scrolled off the screen to left
    """
    
    # Highlight the selected region
    min_pos = min(selection_start_idx_in_text, selection_end_idx_in_text)
    max_pos = max(selection_start_idx_in_text, selection_end_idx_in_text)
        
    # Only highlight visible portion
    visible_selection_start_idx_in_text = max(min_pos, scroll_offset)
    visible_selection_end_idx_in_text = min(max_pos, scroll_offset + max_visible_width)
    
    # Apply highlighting to each visible character
    for i in range(visible_selection_start_idx_in_text, visible_selection_end_idx_in_text):
        # Calculate screen position based on whether we're in sidebar or task area
        if st.focus_manager.is_sidebar_focused():
            # Use base_indent (2) for sidebar to match text_start_pos in edit function
            screen_pos = 2 + (i - scroll_offset)  # Sidebar starts at position 2
            # Ensure we don't highlight beyond sidebar boundary
            if screen_pos > 14:
                break
        else:
            screen_pos = tsk.TASK_INDENT_IN_TASK_PANEL + cat.SIDEBAR_WIDTH + (i - scroll_offset)  # Task position with sidebar offset
            
        if i - scroll_offset >= 0:  # Ensure we only render visible chars
            sf.safe_addstr(stdscr, y, screen_pos, task[text_key][i], curses.A_REVERSE)

def edit(stdscr, entry, text_key, mode, initial_scroll=0):
    """
    A editing wrapper implemented using getch(). It delivers 
    more comprehensive functionalities than getstr() does.
    """
    curses.curs_set(0)
    
    right_frame_pos = st.latest_max_x - 1
    if st.focus_manager.is_sidebar_focused():
        base_indent = 2
        text_start_pos = base_indent
        MAX_DESCRIPTION_LENGTH = cat.MAX_CATEGORY_NAME_LENGTH
        date_length = 0
        date_pos = 15
        max_visible_width = date_pos - base_indent        
    else:
        base_indent = tsk.TASK_INDENT_IN_TASK_PANEL
        text_start_pos = cat.SIDEBAR_WIDTH + base_indent
        MAX_DESCRIPTION_LENGTH = tsk.MAX_TASK_DESCRIPTION_LENGTH    
        date_length = len(entry["date"])
        date_pos = right_frame_pos - date_length - 1  # Only 1 char gap from right frame
        max_visible_width = date_pos - text_start_pos - 1
    
    # Selection state variables
    selection_active = False
    selection_start = -1
    debug_keys = False
    scroll_offset = initial_scroll
    right_limit = 14 if st.focus_manager.is_sidebar_focused() else date_pos - 1

    y = stdscr.getyx()[0]
    
    curses.curs_set(1)
    pr.print_editing_entry(stdscr, entry, text_key, y, is_selected=True, scroll_left=scroll_offset, is_edit_mode=False if mode == pr.add_mode else True)
    if st.focus_manager.is_sidebar_focused():
        cursor_pos_in_text = len(entry[text_key]) 
        sf.safe_move(stdscr, y, base_indent + len(entry[text_key]))
    else:
        sf.safe_move(stdscr, y, cat.SIDEBAR_WIDTH + base_indent + min(max_visible_width, len(entry[text_key])))        
        cursor_pos_in_text = min(max_visible_width, len(entry[text_key]))
    stdscr.refresh()
        
    while True:
        st.latest_max_y, st.latest_max_x = stdscr.getmaxyx()
   
        cursor_y, cursor_x = stdscr.getyx()
        # Limit cursor position to the right boundary
        cursor_x = min(cursor_x, right_limit)

        cursor_pos_in_text = cursor_x - text_start_pos + scroll_offset
        cursor_pos_in_text = min(cursor_pos_in_text, len(entry[text_key]))
        
        # Print plain text first        
        pr.print_editing_entry(stdscr, entry, text_key, y, is_selected=True, scroll_left=scroll_offset, is_edit_mode=False if mode == pr.add_mode else True)
        if  selection_active:
            highlight_selection(stdscr, entry, text_key, y, selection_start, cursor_pos_in_text, scroll_offset, max_visible_width)

        # Move cursor back to correct position
        sf.safe_move(stdscr, cursor_y, cursor_x) 
        
        # Get user input
        ch = stdscr.getch()
        
        # Debug mode - display current key code in top-left corner
        if debug_keys:
            debug_info = f"Key: {ch} | Pos: {cursor_pos_in_text}/{len(entry[text_key])} | Scroll: {scroll_offset}"
            # Save current cursor position
            current_y, current_x = stdscr.getyx()
            # Clear the debug area
            sf.safe_addstr(stdscr, 0, 0, ' ' * min(len(debug_info) + 5, st.latest_max_x))
            # Display debug info
            import todoism.color as clr
            attr = curses.color_pair(clr.get_color_pair_num_by_str_text("red"))
            sf.safe_addstr(stdscr, 0, 0, debug_info, attr)
            # Restore cursor position
            sf.safe_move(stdscr, current_y, current_x)
                
        # Handle key presses
        if ch == 4:  # Toggle debug mode with Ctrl+D
            debug_keys = not debug_keys
            # Clear debug area when turning off
            if not debug_keys:
                current_y, current_x = stdscr.getyx()
                sf.safe_addstr(stdscr, 0, 0, ' ' * st.latest_max_x)
                sf.safe_move(stdscr, current_y, current_x)
            continue
        elif ch == kc.ENTER:  # Enter to complete
            curses.curs_set(0)
            break
        elif ch == kc.ESC:
            curses.curs_set(0)
            if mode == pr.add_mode:
                return ""
            else:
                # Clear selection if active
                selection_active = False
                selection_start = -1
                continue
                
        elif ch == curses.KEY_LEFT:
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
            
            # Only move if not already at the beginning of text
            if cursor_pos_in_text > 0:
                # Calculate new position in text
                new_pos_in_text = cursor_pos_in_text - 1
                
                # Calculate new screen position
                new_x = text_start_pos + (new_pos_in_text - scroll_offset)
                # If cursor would move off-screen left, adjust scroll
                if new_pos_in_text < scroll_offset:
                    scroll_offset = max(0, new_pos_in_text)
                    new_x = text_start_pos
                sf.safe_move(stdscr, y, new_x)
            else:
                # Already at beginning of text
                sf.safe_move(stdscr, y, text_start_pos)
                
        elif ch == curses.KEY_RIGHT:
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                
            # Don't move if already at the absolute end of the text
            if cursor_pos_in_text >= len(entry[text_key]):
                # This is critical - reset cursor to end position but don't change scroll
                new_x = text_start_pos + (len(entry[text_key]) - scroll_offset)
                new_x = min(new_x, right_limit)
                sf.safe_move(stdscr, y, new_x)
                continue
                
            # Move right but strictly check against text length
            new_pos = cursor_pos_in_text + 1
            # Hard limit to prevent going past text end
            new_pos = min(new_pos, len(entry[text_key]))
                
            # Calculate screen position
            new_x = text_start_pos + (new_pos - scroll_offset)
            
            # Only scroll if cursor would move out of view
            if new_x > right_limit:
                # Only scroll the minimum needed to show cursor
                scroll_amount = new_x - right_limit
                scroll_offset += scroll_amount
                new_x = right_limit
            
            sf.safe_move(stdscr, y, new_x)
        
        elif ch == kc.CTRL_LEFT:
            if cursor_pos_in_text <= 0:
                continue
                
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                
            # Find the start of the previous word
            new_pos = move_by_word(entry[text_key], cursor_pos_in_text, -1)
            
            # Check if we're near the end of text (within 5 chars)
            near_end = len(entry[text_key]) - cursor_pos_in_text <= 5
            
            # Only adjust scroll if we're not near the end
            if not near_end and new_pos < scroll_offset + 5:
                scroll_offset = max(0, new_pos - 5)
            elif near_end and new_pos < scroll_offset:
                # If near end but would go out of view, make minimal adjustment
                scroll_offset = new_pos
            
            # Calculate new safe screen position
            new_x = text_start_pos + (new_pos - scroll_offset)
            # Use right_limit instead of hardcoded max_x - 23
            new_x = min(new_x, right_limit)
            
            sf.safe_move(stdscr, y, new_x)
         
        elif ch == kc.CTRL_RIGHT:
            # Don't do anything if already at the end of text
            if cursor_pos_in_text >= len(entry[text_key]):
                new_x = text_start_pos + (len(entry[text_key]) - scroll_offset)
                new_x = min(new_x, date_pos - 1)  # Ensure we respect the gap
                sf.safe_move(stdscr, y, new_x)
                continue
                
            # Find the end of the next word
            new_pos = move_by_word(entry[text_key], cursor_pos_in_text, 1)
            # Only adjust scroll if necessary AND we're not at the end
            if new_pos <= len(entry[text_key]) and new_pos > scroll_offset + max_visible_width:
                # Limited scroll adjustment to prevent large jumps
                scroll_offset = min(
                    new_pos - max_visible_width,
                    len(entry[text_key]) - max_visible_width  # Don't scroll past end
                )
            
            # Calculate new safe screen position
            new_x = text_start_pos + (new_pos - scroll_offset)
            # Use date_pos instead of hardcoded max_x - 23
            new_x = min(new_x, date_pos - 1)
            sf.safe_move(stdscr, y, new_x)
            
        elif ch == kc.CTRL_SHIFT_LEFT:
            if cursor_pos_in_text <= 0:
                continue
                
            # Begin selection if not already active
            if not selection_active:
                selection_active = True
                selection_start = cursor_pos_in_text
            
            # Find the start of the previous word
            new_pos = move_by_word(entry[text_key], cursor_pos_in_text, -1)
            
            # For sidebar (category names), no scrolling needed
            if st.focus_manager.is_sidebar_focused():
                cursor_pos_in_text = new_pos
                new_x = text_start_pos + new_pos
                new_x = min(new_x, 14)  # Hard limit for sidebar
            else:
                # Adjust scroll if needed
                if new_pos < scroll_offset:
                    scroll_offset = max(0, new_pos)
                cursor_pos_in_text = new_pos
                new_x = text_start_pos + (new_pos - scroll_offset)
                new_x = min(new_x, right_limit)
            
            sf.safe_move(stdscr, y, new_x)
            
        elif ch == kc.CTRL_SHIFT_RIGHT:
            if cursor_pos_in_text >= len(entry[text_key]):
                continue
                
            # Begin selection if not already active
            if not selection_active:
                selection_active = True
                selection_start = cursor_pos_in_text
            
            old_pos = cursor_pos_in_text
            # Find the end of the next word
            new_pos = move_by_word(entry[text_key], cursor_pos_in_text, 1)
            
            # For sidebar (category names), no scrolling needed
            if st.focus_manager.is_sidebar_focused():
                cursor_pos_in_text = new_pos
                new_x = text_start_pos + new_pos
                new_x = min(new_x, 14)  # Hard limit for sidebar
            else:
                # Adjust scroll if needed
                if new_pos > scroll_offset + max_visible_width:
                    scroll_offset = scroll_offset + new_pos - old_pos
                cursor_pos_in_text = new_pos
                new_x = text_start_pos + (new_pos - scroll_offset)
                new_x = min(new_x, right_limit)
            
            sf.safe_move(stdscr, y, new_x)

        elif ch == curses.KEY_BACKSPACE or ch == kc.BACKSPACE:  # Backspace
            # Clear selection if active
            if selection_active:
                # Delete the selected text
                min_pos = min(selection_start, cursor_pos_in_text)
                max_pos = max(selection_start, cursor_pos_in_text)
                
                # Properly join text before min_pos with text after max_pos
                entry[text_key] = entry[text_key][:min_pos] + entry[text_key][max_pos:]
                
                selection_active = False
                selection_start = -1
                
                # Adjust scroll if needed
                if min_pos < scroll_offset + 5:
                    scroll_offset = max(0, min_pos - 5)
                
                # Position cursor at deletion point
                new_x = text_start_pos + (min_pos - scroll_offset)
                new_x = min(new_x, right_limit)  # Use right_limit instead of hardcoded value
                
                sf.safe_move(stdscr, y, new_x)
                continue
            
            # Can't backspace past the start
            if cursor_x <= text_start_pos:
                sf.safe_move(stdscr, y, text_start_pos)
                continue
            
            # Save the text length before deletion
            old_length = len(entry[text_key])
            
            # Verify cursor position is valid before deletion
            if cursor_pos_in_text <= 0 or cursor_pos_in_text > old_length:
                # Invalid position - do nothing
                continue
            
            # Delete character before cursor - properly sliced
            entry[text_key] = entry[text_key][:cursor_pos_in_text - 1] + entry[text_key][cursor_pos_in_text:]
            
            # Calculate new cursor position in text
            new_cursor_pos = cursor_pos_in_text - 1
            
            # Special handling for deletion at end of text
            at_end = cursor_pos_in_text >= old_length
            
            # Adjust scroll if needed
            if at_end and scroll_offset > 0:
                # When deleting from end of text, adjust scroll to keep visible area stable
                scroll_offset = max(0, scroll_offset - 1)
            elif new_cursor_pos < scroll_offset + 5 and scroll_offset > 0:
                # Standard adjustment for deleting near left edge of view
                scroll_offset = max(0, new_cursor_pos - 5)
            
            # Calculate correct screen position after deletion
            new_x = text_start_pos + (new_cursor_pos - scroll_offset)
            
            # Ensure position is valid
            new_x = max(text_start_pos, min(new_x, right_limit))
            
            sf.safe_move(stdscr, y, new_x)
        
        elif 32 <= ch < 127:  # Printable char
            if st.focus_manager.is_sidebar_focused() and len(entry[text_key]) >= MAX_DESCRIPTION_LENGTH:
                continue
                
            # Check maximum length for regular tasks
            if len(entry[text_key]) >= MAX_DESCRIPTION_LENGTH and not selection_active:
                continue
                
            # If a selection is active, replace it with the typed character
            if selection_active:
                # Get selection bounds with safety checks
                min_pos = min(selection_start, cursor_pos_in_text)
                max_pos = max(selection_start, cursor_pos_in_text)
                
                # Ensure bounds are valid
                min_pos = max(0, min(min_pos, len(entry[text_key])))
                max_pos = max(0, min(max_pos, len(entry[text_key])))
                
                if min_pos != max_pos:  # Only if there's an actual selection
                    entry[text_key] = entry[text_key][:min_pos] + chr(ch) + entry[text_key][max_pos:]
                    
                    # Position cursor after the inserted character
                    cursor_pos_in_text = min_pos + 1
                    
                    # Adjust scroll if needed to keep cursor visible
                    if min_pos < scroll_offset:
                        scroll_offset = min_pos
                        
                    # Clear selection state
                    selection_active = False
                    selection_start = -1
                    
                    # Calculate screen position
                    new_x = text_start_pos + (cursor_pos_in_text - scroll_offset)
                    new_x = min(new_x, right_limit)
                    
                    sf.safe_move(stdscr, y, new_x)
                    continue
                
            # Ensure cursor position is valid before insertion
            if cursor_pos_in_text < 0 or cursor_pos_in_text > len(entry[text_key]):
                cursor_pos_in_text = min(max(0, cursor_pos_in_text), len(entry[text_key]))
            
            # Keep track of whether we're at the end of text before insertion
            at_end_of_text = cursor_pos_in_text == len(entry[text_key])
            
            # Insert character at the correct position
            entry[text_key] = entry[text_key][:cursor_pos_in_text] + chr(ch) + entry[text_key][cursor_pos_in_text:]            
            # Calculate new cursor position in text
            new_cursor_pos = cursor_pos_in_text + 1
            
            at_end_of_text = cursor_pos_in_text == len(entry[text_key])
            
            # Recalculate screen boundaries with exactly 1 space gap
            if not st.focus_manager.is_sidebar_focused():
                date_length = len(entry["date"])
                date_pos = right_frame_pos - date_length - 1  # Position where date starts (with 1 char gap)
                max_visible_width = date_pos - (text_start_pos)  # Total spaces available for text
                right_limit = date_pos - 1  # Position of the 1 char gap
            else:
                date_length = 0
                date_pos = 15
                max_visible_width = date_pos - base_indent
                 
            if at_end_of_text:
                # When we're at the end of text and need to scroll:
                if new_cursor_pos > scroll_offset + max_visible_width:
                    # First update the scroll position before updating cursor
                    scroll_offset = new_cursor_pos - max_visible_width
                
                # Always update cursor position after any scroll adjustment
                cursor_pos_in_text = new_cursor_pos
            elif cursor_pos_in_text - scroll_offset >= max_visible_width - 1:
                # When cursor is at the edge of visible area but not at end of text
                # We need to scroll by 1 to show the newly inserted character
                scroll_offset += 1
                cursor_pos_in_text = new_cursor_pos
            else:
                # Regular case - just update cursor position
                cursor_pos_in_text = new_cursor_pos
            
            # Calculate new cursor X position with consistent gap
            new_x = text_start_pos + (new_cursor_pos - scroll_offset)
            
            # Safety check to ensure we never go beyond right_limit
            new_x = min(new_x, right_limit)
            
            sf.safe_move(stdscr, y, new_x)
            
            # Extra check after character insertion
            if st.focus_manager.is_sidebar_focused():
                # Recalculate and verify cursor position doesn't exceed sidebar
                new_x = text_start_pos + (new_cursor_pos - scroll_offset)
                if new_x > 14:
                    # Adjust scroll to keep cursor within sidebar
                    scroll_offset += (new_x - 14)
                    new_x = 14
                
                # Hard limit for cursor in sidebar mode
                new_x = min(new_x, 14)
                sf.safe_move(stdscr, y, new_x)
        
        elif ch == kc.ALT_LEFT:
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                
            cursor_pos_in_text = 0
            scroll_offset = 0
            # Position cursor at beginning
            sf.safe_move(stdscr, y, text_start_pos)
            
        # Alt+Right to jump to end of text
        elif ch == kc.ALT_RIGHT:
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                
            cursor_pos_in_text = len(entry[text_key])
            # For long text, adjust scroll to show the end of text
            if len(entry[text_key]) > max_visible_width:
                # Calculate scroll needed to position cursor at right side with proper buffer
                scroll_offset = max(0, len(entry[text_key]) - max_visible_width)
                # Position cursor at end with proper right side alignment
                new_x = text_start_pos + max_visible_width
                new_x = min(new_x, right_limit)
            else:
                # For short text, no scroll needed
                scroll_offset = 0
                new_x = text_start_pos + len(entry[text_key])
                
            # Ensure we respect the right boundary
            new_x = min(new_x, right_limit)
            sf.safe_move(stdscr, y, new_x)
            
    return entry[text_key]

def handle_edit(stdscr, task_list):
    sf.safe_move(stdscr, st.current_task_row, cat.SIDEBAR_WIDTH + tsk.TASK_INDENT_IN_TASK_PANEL)
    stdscr.refresh()
    current_task_idx = st.current_task_id - 1
    st.filtered_tasks[current_task_idx]["description"] = edit(
        stdscr, 
        st.filtered_tasks[current_task_idx],
        "description",
        pr.edit_mode
    )
    if st.filtered_tasks[current_task_idx]["description"] == "":
        task_uuid = st.filtered_tasks[current_task_idx]["uuid"]
        task_list = tsk.delete_task_by_uuid(task_list, task_uuid)
        if st.searching:
            st.filtered_tasks = [task for task in st.filtered_tasks if task["uuid"] != task_uuid]
        else:
            st.filtered_tasks = tsk.get_tasks_by_category_id(task_list, st.current_category_id)
        st.task_cnt = len(st.filtered_tasks)
        nv.post_deletion_update(st.task_cnt + 1)
    tsk.save_tasks(task_list)
    return task_list
    