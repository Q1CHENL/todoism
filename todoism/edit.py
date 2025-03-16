import curses
import todoism.print as pr
import todoism.task as tsk
import todoism.navigate as nv
import todoism.keycode as kc
import todoism.state as st

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

def render_edit_line(stdscr, task, y, scroll_offset, max_visible_width, cursor_pos_in_text=None):
    """Helper function to render a task being edited with appropriate scrolling and styling"""
    max_y, max_x = stdscr.getmaxyx()
    right_frame_pos = max_x - 1
    
    # Turn off highlight before drawing frame elements
    stdscr.attroff(curses.color_pair(1))
    
    stdscr.addstr(0, 0, "┌")  # Top-left corner
    for x in range(1, 15):
        stdscr.addstr(0, x, "─")  # Top horizontal line for sidebar
    stdscr.addstr(0, 15, "┬")  
    
    # Add right frame character with highlight off
    if not st.focus_manager.is_sidebar_focused():
        stdscr.addstr(y, right_frame_pos, '│')
        stdscr.attron(curses.color_pair(1))
    
    result = pr.render_task(
        stdscr=stdscr,
        task=task,
        y=y,
        is_selected=True,
        scroll_offset=scroll_offset,
        max_x=max_x,
        cursor_pos=cursor_pos_in_text,
        is_edit_mode=True
    )
    
    # Add extra protection for sidebar mode
    if st.focus_manager.is_sidebar_focused() and result is not None and result > 14:
        return 14
    
    return result

def highlight_selection(stdscr, task, y, start_pos, end_pos, scroll_offset):
    """Highlight selected text region"""
    # Highlight the selected region
    min_pos = min(start_pos, end_pos)
    max_pos = max(start_pos, end_pos)
    
    # Only highlight visible portion
    visible_start = max(min_pos, scroll_offset)
    visible_end = max_pos
    
    # Apply highlighting to each visible character
    for i in range(visible_start, visible_end):
        # Calculate screen position based on whether we're in sidebar or task area
        if st.focus_manager.is_sidebar_focused():
            # Use base_indent (2) for sidebar to match text_start_pos in edit function
            screen_pos = 2 + (i - scroll_offset)  # Sidebar starts at position 2
            # Ensure we don't highlight beyond sidebar boundary
            if screen_pos > 14:  # Sidebar width limit
                break
        else:
            screen_pos = tsk.TASK_INDENT_IN_TASK_PANEL + 16 + (i - scroll_offset)  # Task position with sidebar offset
            
        if i - scroll_offset >= 0:  # Ensure we only render visible chars
            try:
                stdscr.addstr(y, screen_pos, task['description'][i], curses.A_REVERSE)
            except curses.error:
                # Skip characters that would go past the edge of the screen
                pass

def edit(stdscr, task, mode, initial_scroll=0, initial_cursor_pos=None):
    """
    A editing wrapper implemented using getch(). It delivers 
    more comprehensive functionalities than getstr() does.
    """
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()
    right_frame_pos = max_x - 1
    
    # Standardize indent calculations
    if st.focus_manager.is_sidebar_focused():
        sidebar_width = 0
        base_indent = 2
        text_start_pos = base_indent
        import todoism.category as cat
        MAX_DESCRIPTION_LENGTH = cat.MAX_CATEGORY_NAME_LENGTH
    else:
        sidebar_width = 16
        base_indent = tsk.TASK_INDENT_IN_TASK_PANEL
        text_start_pos = sidebar_width + base_indent
        MAX_DESCRIPTION_LENGTH = tsk.MAX_TASK_DESCRIPTION_LENGTH
    
    # Selection state variables
    selection_active = False
    selection_start = -1
    debug_keys = False
    scroll_offset = initial_scroll
    
    # Initialize cursor position
    if initial_cursor_pos is not None:
        cursor_pos_in_text = min(initial_cursor_pos, len(task['description']))
    else:
        cursor_pos_in_text = len(task['description'])  # Start at end of text for new tasks
    
    # Calculate available width
    if st.focus_manager.is_sidebar_focused():
        date_length = 0
        date_pos = 15
        max_visible_width = date_pos - base_indent
    else:
        date_length = len(task['date'])
        date_pos = right_frame_pos - date_length - 1  # Only 1 char gap from right frame
        max_visible_width = date_pos - text_start_pos - 1
    
    y = stdscr.getyx()[0]
    
    # Initial render with proper offset
    target_x = render_edit_line(stdscr, task, y, scroll_offset, max_visible_width, cursor_pos_in_text)
    stdscr.move(y, target_x)
    stdscr.refresh()
        
    while True:
        # Get current position
        y, x = stdscr.getyx()
        max_y, max_x = stdscr.getmaxyx()
        
        # Ensure cursor never appears beyond sidebar for sidebar editing
        if st.focus_manager.is_sidebar_focused() and x > 14:
            # Force cursor back into valid sidebar region if it somehow gets displaced
            x = min(14, text_start_pos + len(task['description']))
            stdscr.move(y, x)
        
        # Clear the edit line WITHOUT clearing the category at the same height
        if st.focus_manager.is_sidebar_focused():
            # For sidebar editing, clear just the sidebar area
            stdscr.move(y, 0)
            # Preserve left frame
            stdscr.addch(y, 0, '│')
            
            # Clear character by character only in sidebar area (columns 1-14)
            for j in range(1, 15):  # Clear columns 1-14, preserving left frame
                stdscr.addch(y, j, ' ')
            
            # Restore the separator after clearing
            stdscr.addch(y, 15, '│')
            
            # IMPORTANT: Immediately draw the text after clearing
            # This ensures the text is always visible without flicker
            if len(task['description']) > 0:
                # Add 2-space indent for category names (account for left frame)
                visible_text = task['description'][scroll_offset:scroll_offset + max_visible_width]
                stdscr.addstr(y, base_indent, visible_text)
            
            # Move cursor to the correct position
            cursor_x = text_start_pos + min(len(task['description']) - scroll_offset, max_visible_width)
            cursor_x = max(text_start_pos, min(cursor_x, 14))  # Hard limit cursor position in sidebar
            stdscr.move(y, cursor_x)
            
            # Force screen update to stabilize display
            stdscr.refresh()
            
        else:
            # Only clear from the separator onwards, preserving sidebar content
            sidebar_width = 16  # Always use 16 here to preserve sidebar content
            
            # Move to the separator and clear only to the right
            stdscr.move(y, 16)  # Position just after separator
            stdscr.clrtoeol()
            
            # Redraw vertical separator
            stdscr.addstr(y, 15, '│')
            
            # Redraw task ID
            stdscr.addstr(y, sidebar_width, f"{task['id']:2d} ")
        
        # Recalculate with current screen dimensions
        if st.focus_manager.is_sidebar_focused():
            date_pos = 15  # End of sidebar area
            max_visible_width = date_pos - base_indent
        else:
            date_pos = right_frame_pos - date_length - 1
            max_visible_width = date_pos - text_start_pos - 1
            
        right_limit = date_pos - 1
        
        # Additional bound check for sidebar
        if st.focus_manager.is_sidebar_focused():
            right_limit = min(14, date_pos - 1)  # Hard limit at the sidebar boundary
        
        # Calculate cursor position in text with bounds checking
        cursor_pos_in_text = max(0, min(x - text_start_pos + scroll_offset, len(task['description'])))
        
        # Render the edit line with current scroll offset
        target_x = render_edit_line(stdscr, task, y, scroll_offset, max_visible_width, cursor_pos_in_text)
        
        # Add selection highlighting if active
        if selection_active:
            highlight_selection(stdscr, task, y, selection_start, cursor_pos_in_text, scroll_offset)
        
        # Redraw the separator
        if st.focus_manager.is_sidebar_focused():
            stdscr.addstr(y, 15, '│')
        
        # Position cursor
        stdscr.move(y, target_x)
        
        # For sidebar mode: ensure cursor stays in valid position after rendering
        if st.focus_manager.is_sidebar_focused():
            current_x = stdscr.getyx()[1]
            if current_x > 14:
                stdscr.move(y, 14)
        
        # Get user input
        ch = stdscr.getch()
        
        # Debug mode - display current key code in top-left corner
        if debug_keys:
            debug_info = f"Key: {ch} | Pos: {cursor_pos_in_text}/{len(task['description'])} | Scroll: {scroll_offset}"
            # Save current cursor position
            current_y, current_x = stdscr.getyx()
            # Clear the debug area
            stdscr.addstr(0, 0, ' ' * min(len(debug_info) + 5, max_x))
            # Display debug info
            stdscr.attron(curses.color_pair(4))  # Red color for visibility
            stdscr.addstr(0, 0, debug_info)
            stdscr.attroff(curses.color_pair(4))
            # Restore cursor position
            stdscr.move(current_y, current_x)
                
        # Handle key presses
        if ch == 4:  # Toggle debug mode with Ctrl+D
            debug_keys = not debug_keys
            # Clear debug area when turning off
            if not debug_keys:
                current_y, current_x = stdscr.getyx()
                stdscr.addstr(0, 0, ' ' * max_x)
                stdscr.move(current_y, current_x)
            continue
        elif ch == kc.ENTER:  # Enter to complete
            break
        elif ch == kc.ESC:
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
                stdscr.move(y, new_x)
            else:
                # Already at beginning of text
                stdscr.move(y, text_start_pos)
                
        elif ch == curses.KEY_RIGHT:
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                
            # Don't move if already at the absolute end of the text
            if cursor_pos_in_text >= len(task['description']):
                # This is critical - reset cursor to end position but don't change scroll
                new_x = text_start_pos + (len(task['description']) - scroll_offset)
                new_x = min(new_x, right_limit)
                stdscr.move(y, new_x)
                continue
                
            # Move right but strictly check against text length
            new_pos = cursor_pos_in_text + 1
            # Hard limit to prevent going past text end
            new_pos = min(new_pos, len(task['description']))
                
            # Calculate screen position
            new_x = text_start_pos + (new_pos - scroll_offset)
            
            # Only scroll if cursor would move out of view
            if new_x > right_limit:
                # Only scroll the minimum needed to show cursor
                scroll_amount = new_x - right_limit
                scroll_offset += scroll_amount
                new_x = right_limit
            
            stdscr.move(y, new_x)
        
        elif ch == kc.CTRL_LEFT:
            if cursor_pos_in_text <= 0:
                continue
                
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                
            # Find the start of the previous word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, -1)
            
            # KEY FIX: Check if we're near the end of text (within 5 chars)
            near_end = len(task['description']) - cursor_pos_in_text <= 5
            
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
            
            stdscr.move(y, new_x)
         
        elif ch == kc.CTRL_RIGHT:
            # Don't do anything if already at the end of text
            if cursor_pos_in_text >= len(task['description']):
                # KEY FIX: Explicitly stabilize position at the end
                new_x = text_start_pos + (len(task['description']) - scroll_offset)
                new_x = min(new_x, date_pos - 1)  # Ensure we respect the gap
                stdscr.move(y, new_x)
                continue
                
            # Find the end of the next word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, 1)
            
            # Only adjust scroll if necessary AND we're not at the end
            if new_pos < len(task['description']) and new_pos > scroll_offset + max_visible_width - 5:
                # Limited scroll adjustment to prevent large jumps
                scroll_offset = min(
                    new_pos - max_visible_width + 5,
                    len(task['description']) - max_visible_width  # Don't scroll past end
                )
                # Ensure scroll_offset is never negative
                scroll_offset = max(0, scroll_offset)
            
            # Calculate new safe screen position
            new_x = text_start_pos + (new_pos - scroll_offset)
            # Use date_pos instead of hardcoded max_x - 23
            new_x = min(new_x, date_pos - 1)
            
            stdscr.move(y, new_x)
            
        elif ch == kc.CTRL_SHIFT_LEFT:
            if cursor_pos_in_text <= 0:
                continue
                
            # Begin selection if not already active
            if not selection_active:
                selection_active = True
                selection_start = cursor_pos_in_text
            
            # Find the start of the previous word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, -1)
            
            # For sidebar (category names), no scrolling needed
            if st.focus_manager.is_sidebar_focused():
                cursor_pos_in_text = new_pos
                new_x = text_start_pos + new_pos
                new_x = min(new_x, 14)  # Hard limit for sidebar
            else:
                # Adjust scroll if needed
                if new_pos < scroll_offset + 5:
                    scroll_offset = max(0, new_pos - 5)
                cursor_pos_in_text = new_pos
                new_x = text_start_pos + (new_pos - scroll_offset)
                new_x = min(new_x, right_limit)
            
            stdscr.move(y, new_x)
            
        elif ch == kc.CTRL_SHIFT_RIGHT:
            if cursor_pos_in_text >= len(task['description']):
                continue
                
            # Begin selection if not already active
            if not selection_active:
                selection_active = True
                selection_start = cursor_pos_in_text
            
            # Find the end of the next word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, 1)
            
            # For sidebar (category names), no scrolling needed
            if st.focus_manager.is_sidebar_focused():
                cursor_pos_in_text = new_pos
                new_x = text_start_pos + new_pos
                new_x = min(new_x, 14)  # Hard limit for sidebar
            else:
                # Adjust scroll if needed
                if new_pos > scroll_offset + max_visible_width - 5:
                    scroll_offset = new_pos - max_visible_width + 5
                cursor_pos_in_text = new_pos
                new_x = text_start_pos + (new_pos - scroll_offset)
                new_x = min(new_x, right_limit)
            
            stdscr.move(y, new_x)
        
        elif ch == curses.KEY_BACKSPACE or ch == kc.BACKSPACE:  # Backspace
            # Clear selection if active
            if selection_active:
                # Delete the selected text
                min_pos = min(selection_start, cursor_pos_in_text)
                max_pos = max(selection_start, cursor_pos_in_text)
                
                # Fixed concatenation - properly join text before min_pos with text after max_pos
                task['description'] = task['description'][:min_pos] + task['description'][max_pos:]
                
                selection_active = False
                selection_start = -1
                
                # Adjust scroll if needed
                if min_pos < scroll_offset + 5:
                    scroll_offset = max(0, min_pos - 5)
                
                # Position cursor at deletion point
                new_x = text_start_pos + (min_pos - scroll_offset)
                new_x = min(new_x, right_limit)  # Use right_limit instead of hardcoded value
                
                stdscr.move(y, new_x)
                continue
            
            # Can't backspace past the start
            if x <= text_start_pos:
                stdscr.move(y, text_start_pos)
                continue
            
            # Save the text length before deletion
            old_length = len(task['description'])
            
            # Verify cursor position is valid before deletion
            if cursor_pos_in_text <= 0 or cursor_pos_in_text > old_length:
                # Invalid position - do nothing
                continue
            
            # Delete character before cursor - properly sliced
            task['description'] = task['description'][:cursor_pos_in_text - 1] + task['description'][cursor_pos_in_text:]
            
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
            
            stdscr.move(y, new_x)
        
        elif 32 <= ch < 127:  # Printable char
            # IMPROVED CHECK: For sidebar (categories), enforce strict character limit 
            # to prevent visual glitches when the limit is reached
            if st.focus_manager.is_sidebar_focused() and len(task['description']) >= MAX_DESCRIPTION_LENGTH:
                # Skip character completely - no visual feedback
                continue
                
            # Check maximum length for regular tasks
            if len(task['description']) >= MAX_DESCRIPTION_LENGTH and not selection_active:
                continue
                
            # If a selection is active, replace it with the typed character
            if selection_active:
                # Get selection bounds with safety checks
                min_pos = min(selection_start, cursor_pos_in_text)
                max_pos = max(selection_start, cursor_pos_in_text)
                
                # Ensure bounds are valid
                min_pos = max(0, min(min_pos, len(task['description'])))
                max_pos = max(0, min(max_pos, len(task['description'])))
                
                if min_pos != max_pos:  # Only if there's an actual selection
                    task['description'] = task['description'][:min_pos] + chr(ch) + task['description'][max_pos:]
                    
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
                    
                    stdscr.move(y, new_x)
                    continue
                
            # Ensure cursor position is valid before insertion
            if cursor_pos_in_text < 0 or cursor_pos_in_text > len(task['description']):
                cursor_pos_in_text = min(max(0, cursor_pos_in_text), len(task['description']))
            
            # Keep track of whether we're at the end of text before insertion
            at_end_of_text = cursor_pos_in_text == len(task['description'])
            
            # Insert character at the correct position
            task['description'] = task['description'][:cursor_pos_in_text] + chr(ch) + task['description'][cursor_pos_in_text:]
            
            # Calculate new cursor position in text
            new_cursor_pos = cursor_pos_in_text + 1
            
            at_end_of_text = cursor_pos_in_text == len(task['description'])
            
            # Recalculate screen boundaries with exactly 1 space gap
            if not st.focus_manager.is_sidebar_focused():
                date_length = len(task['date'])
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
            
            stdscr.move(y, new_x)
            
            # IMPROVED SIDEBAR HANDLING: Add extra check after character insertion
            if st.focus_manager.is_sidebar_focused():
                # Recalculate and verify cursor position doesn't exceed sidebar
                new_x = text_start_pos + (new_cursor_pos - scroll_offset)
                if new_x > 14:
                    # Adjust scroll to keep cursor within sidebar
                    scroll_offset += (new_x - 14)
                    new_x = 14
                
                # Hard limit for cursor in sidebar mode
                new_x = min(new_x, 14)
                stdscr.move(y, new_x)
        
        # Alt+Left to jump to beginning of text (handle recorded keycode)
        elif ch == kc.ALT_LEFT:
            # If ESC (27), need to check if it's followed by proper sequence
            if ch == kc.ESC:
                # Check for ESC sequence
                next_ch = stdscr.getch()
                if next_ch != ord('[') and next_ch != 91:  # Check for '[' character
                    continue
                    
                direction_ch = stdscr.getch()
                if direction_ch != 49 and direction_ch != ord('1'):  # Not part of Alt+Left sequence
                    continue
                    
                final_ch = stdscr.getch()
                if final_ch != 59 and final_ch != ord(';'):  # Not part of Alt+Left sequence
                    continue
                    
                mod_ch = stdscr.getch()
                if mod_ch != 51 and mod_ch != ord('3'):  # Not Alt modifier (3)
                    continue
                    
                arrow_ch = stdscr.getch()
                if arrow_ch != 68 and arrow_ch != ord('D'):  # Not left arrow ('D')
                    continue
            
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                
            # Jump to beginning of text
            cursor_pos_in_text = 0
            
            # Reset scroll offset to show beginning of text
            scroll_offset = 0
            
            # Position cursor at beginning
            stdscr.move(y, text_start_pos)
            
        # Alt+Right to jump to end of text (handle recorded keycode)
        elif ch == kc.ALT_RIGHT:  # Various codes for Alt+Right
            # If ESC (27), need to check if it's followed by proper sequence
            if ch == kc.ESC:
                # Check for ESC sequence
                next_ch = stdscr.getch()
                if next_ch != ord('[') and next_ch != 91:  # Check for '[' character
                    continue
                    
                direction_ch = stdscr.getch()
                if direction_ch != 49 and direction_ch != ord('1'):  # Not part of Alt+Right sequence
                    continue
                    
                final_ch = stdscr.getch()
                if final_ch != 59 and final_ch != ord(';'):  # Not part of Alt+Right sequence
                    continue
                    
                mod_ch = stdscr.getch()
                if mod_ch != 51 and mod_ch != ord('3'):  # Not Alt modifier (3)
                    continue
                    
                arrow_ch = stdscr.getch()
                if arrow_ch != 67 and arrow_ch != ord('C'):  # Not right arrow ('C')
                    continue
            
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                
            # Jump to end of text
            cursor_pos_in_text = len(task['description'])
            
            # For long text, adjust scroll to show the end of text
            if len(task['description']) > max_visible_width:
                # Calculate scroll needed to position cursor at right side with proper buffer
                scroll_offset = max(0, len(task['description']) - max_visible_width)
                
                # Position cursor at end with proper right side alignment
                new_x = text_start_pos + max_visible_width
                new_x = min(new_x, right_limit)
            else:
                # For short text, no scroll needed
                scroll_offset = 0
                new_x = text_start_pos + len(task['description'])
                
            # Ensure we respect the right boundary
            new_x = min(new_x, right_limit)
            stdscr.move(y, new_x)
            
    return task['description']

def edit_and_save(stdscr, task_list, id, row, start, end, y, x, max_capacity):
    """Edit task or category with improved cursor positioning and scrolling behavior"""
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()
    
    # Get description length
    description_length = len(task_list[id - 1]['description'])
    date_length = len(task_list[id - 1]['date'])
    
    # Calculate exact space available for text (accounting for date + gap)
    date_pos = max_x - date_length - 1  # -1 for exactly one character gap before date
    available_width = date_pos - (tsk.TASK_INDENT_IN_TASK_PANEL + 16) - 1  # -1 ensures the gap is preserved
    
    # Always initialize with scroll_offset = 0 to show beginning of text
    scroll_offset = 0
    
    # Position cursor differently based on text length:
    if description_length <= available_width:
        # For short tasks (text fits): position at end of text
        cursor_x = tsk.TASK_INDENT_IN_TASK_PANEL + 16 + description_length
    else:
        # For long tasks: position at end of visible portion
        cursor_x = tsk.TASK_INDENT_IN_TASK_PANEL + 16 + available_width
    
    # Make sure cursor position is within screen bounds
    cursor_x = min(cursor_x, date_pos - 1)  # Ensure exactly one char gap
    
    # Calculate cursor position in text
    cursor_pos_in_text = cursor_x - (tsk.TASK_INDENT_IN_TASK_PANEL + 16) + scroll_offset
    
    # Set cursor at the calculated position
    stdscr.move(y, cursor_x)
    
    # Initialize the edit function with the appropriate scroll offset and cursor position
    task_list[id - 1]['description'] = edit(
        stdscr, 
        task_list[id - 1], 
        pr.edit_mode, 
        initial_scroll=scroll_offset,
        initial_cursor_pos=cursor_pos_in_text
    )
    
    # Handle task deletion if description is empty
    if task_list[id - 1]['description'] == "":
        del task_list[id - 1]
        tsk.reassign_task_ids(task_list)
        nv.post_deletion_update(len(task_list) + 1)
    
    # Save changes
    tsk.save_tasks(task_list)
    return id, row, start, end

