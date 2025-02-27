import curses
import todoism.print as pr
import todoism.task as tsk


indent = 7
max_task_count = 99

def reid(task_list):
    """Reassign ids to every task in the list"""
    for i, t in enumerate(task_list):
        t['id'] = i + 1


def is_view_fully_packed(start, end, capacity):
    """indicates whether the current view is completely filled with tasks"""
    return end - start + 1 >= capacity


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

def edit(stdscr, task, mode):
    """
    A editing wrapper implemented using getch(). It delivers 
    more comprehensive functionalities than getstr() does.
    """
    # Selection state variables
    selection_active = False
    selection_start = -1
    # Add debug mode flag
    debug_keys = False
    
    while True:
        y, x = stdscr.getyx()
        ch = stdscr.getch()
        
        # Get relative cursor position in the description text
        cursor_pos_in_text = x - indent
        
        # Debug mode to show key codes
        if debug_keys:
            stdscr.addstr(0, 0, f"Key pressed: {ch}    ")
            stdscr.refresh()
            
        # Toggle debug mode with Ctrl+D (usually code 4)
        if ch == 4:
            debug_keys = not debug_keys
            continue
            
        if ch == 10:  # Enter to complete
            break
        elif ch == 27:  # ESC
            if mode == pr.add_mode:
                return ""
            else:
                # Clear selection if active
                selection_active = False
                selection_start = -1
                pr.print_task_mode(stdscr, task, y, mode)
                stdscr.move(y, x)
                
        elif ch == curses.KEY_LEFT:
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                pr.print_task_mode(stdscr, task, y, mode)
            # Cursor remains still or moves left
            new_x = indent if x <= indent else x - 1
            stdscr.move(y, new_x)
            
        elif ch == curses.KEY_RIGHT:
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                pr.print_task_mode(stdscr, task, y, mode)
            # Move right but don't go past the end of description
            stdscr.move(y, x + 1 if x < indent + len(task['description']) else indent + len(task['description']))
        
        # Ctrl+Left to move to previous word (without selection)
        elif ch == 554:
            if cursor_pos_in_text <= 0:
                continue
                
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                pr.print_task_mode(stdscr, task, y, mode)
                
            # Find the start of the previous word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, -1)
            stdscr.move(y, new_pos + indent)
            
        # Ctrl+Right to move to next word (without selection)
        elif ch == 569:
            if cursor_pos_in_text >= len(task['description']):
                continue
                
            # Clear selection if active
            if selection_active:
                selection_active = False
                selection_start = -1
                pr.print_task_mode(stdscr, task, y, mode)
                
            # Find the end of the next word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, 1)
            stdscr.move(y, new_pos + indent)
            
        # Try multiple common key code patterns for Ctrl+Shift+Left
        elif ch in [545, 547, 443, 541, 71, 555]:
            if cursor_pos_in_text <= 0:
                continue
                
            if not selection_active:
                selection_active = True
                selection_start = cursor_pos_in_text
                
            # Find the start of the previous word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, -1)
            
            # Highlight selection
            if selection_active:
                pr.print_task_mode(stdscr, task, y, mode)
                # Highlight the selected region
                min_pos = min(selection_start, new_pos)
                max_pos = max(selection_start, new_pos)
                for i in range(min_pos, max_pos):
                    stdscr.addstr(y, indent + i, task['description'][i], curses.A_REVERSE)
            
            stdscr.move(y, new_pos + indent)
            
        # Try multiple common key code patterns for Ctrl+Shift+Right
        elif ch in [560, 562, 444, 556, 86, 570]:
            if cursor_pos_in_text >= len(task['description']):
                continue
                
            if not selection_active:
                selection_active = True
                selection_start = cursor_pos_in_text
                
            # Find the end of the next word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, 1)
            
            # Highlight selection
            if selection_active:
                pr.print_task_mode(stdscr, task, y, mode)
                # Highlight the selected region
                min_pos = min(selection_start, new_pos)
                max_pos = max(selection_start, new_pos)
                for i in range(min_pos, max_pos):
                    stdscr.addstr(y, indent + i, task['description'][i], curses.A_REVERSE)
            
            stdscr.move(y, new_pos + indent)
            
        # Try multiple common key code patterns for Ctrl+Shift+Backspace or Ctrl+W
        elif ch in [523, 527, 23, 127]:
            if cursor_pos_in_text <= 0:
                continue
                
            # Find the start of the previous word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, -1)
            
            # Delete characters from new position to current position
            task['description'] = task['description'][:new_pos] + task['description'][cursor_pos_in_text:]
            pr.print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, new_pos + indent)
            
            # Clear selection state
            selection_active = False
            selection_start = -1
            
        # Try multiple common key code patterns for Ctrl+Shift+Delete or Ctrl+Alt+D
        elif ch in [524, 528, 127, 4]:
            if cursor_pos_in_text >= len(task['description']):
                continue
                
            # Find the end of the next word
            new_pos = move_by_word(task['description'], cursor_pos_in_text, 1)
            
            # Delete characters from current position to new position
            task['description'] = task['description'][:cursor_pos_in_text] + task['description'][new_pos:]
            pr.print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x)
            
            # Clear selection state
            selection_active = False
            selection_start = -1
            
        elif ch == curses.KEY_BACKSPACE or ch == 127:  # Delete
            # Clear selection if active
            if selection_active:
                # Delete the selected text
                min_pos = min(selection_start, cursor_pos_in_text)
                max_pos = max(selection_start, cursor_pos_in_text)
                task['description'] = task['description'][:min_pos] + task['description'][max_pos:]
                selection_active = False
                selection_start = -1
                pr.print_task_mode(stdscr, task, y, mode)
                stdscr.move(y, min_pos + indent)
                continue
                
            if x <= indent:
                stdscr.move(y, indent)  # cursor remains still
                continue
            # -1 because deleting the char before the cursor
            task['description'] = task['description'][:x - indent - 1] + task['description'][x - indent:]
            pr.print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x - 1)
            
        elif 32 <= ch < 127:  # Printable char
            # If a selection is active, replace it with the typed character
            if selection_active:
                min_pos = min(selection_start, cursor_pos_in_text)
                max_pos = max(selection_start, cursor_pos_in_text)
                task['description'] = task['description'][:min_pos] + chr(ch) + task['description'][max_pos:]
                selection_active = False
                selection_start = -1
                pr.print_task_mode(stdscr, task, y, mode)
                stdscr.move(y, min_pos + indent + 1)
                continue
                
            task['description'] = task['description'][:x - indent] + chr(ch) + task['description'][x - indent:]
            pr.print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x + 1)
            
    return task['description']

def edit_and_save(stdscr, task_list, id, row, start, end, y, x, max_capacity):
    stdscr.move(y, x)
    task_list[id - 1]['description'] = edit(stdscr, task_list[id - 1], pr.edit_mode)
    if task_list[id - 1]['description'] == "":
        del task_list[id - 1]
        reid(task_list)
        id, row, start, end = post_deletion_update(id, row, start, end, len(task_list) + 1, max_capacity)
    tsk.save_tasks(task_list, tsk.tasks_file_path)
    return id, row, start, end

def post_deletion_update(current_id, current_row, start, end, prev_task_cnt, max_capacity):
    """
    Update the current view after deletion: 
    1. 2x Backspaces
    2. edit to empty 
    3. command del
    
    There are 4 senarios where the view is fully packed with tasks before deletion:
    
                                       │       │                                       │       │
    Senario 1: ┌───────┐    Senario 2: ├───────┤    Senario 3: ┌───────┐    Senario 4: ├───────┤
               ├───────┤               ├───────┤               ├───────┤               ├───────┤
               ├───────┤               ├───────┤               ├───────┤               ├───────┤   
               ├───────┤               ├───────┤               ├───────┤               ├───────┤
               └───────┘               └───────┘               ├───────┤               ├───────┤                  
                                                               │       │               │       │
    And the view update rules are similar to the Apple Reminder's
                
                
    There is only 1 senario where the view is not fully packed with tasks:
    
    Senario 5: ┌───────┐
               ├───────┤
               ├───────┤
               │       │
               └───────┘
    """
    if is_view_fully_packed(start, end, max_capacity):
        # Senarios 1
        if prev_task_cnt == max_capacity:
            # delete the last task, otherwise the row and id both remains unchanged
            if current_id == end:
                current_row = current_row - 1
                current_id = current_id - 1
            end = end - 1
        # Senario 2
        elif prev_task_cnt == end and prev_task_cnt > max_capacity:
            start = start - 1
            end = end - 1
            current_id = current_id - 1
        # Senario 3 and 4 does not lead to any change
    
    # Senario 5
    else:
        end = end - 1
        if current_id == prev_task_cnt:
            current_row = current_row - 1
            current_id = current_id - 1
    return current_id, current_row, start, end