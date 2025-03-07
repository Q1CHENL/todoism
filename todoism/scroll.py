def keydown_update(start, end, current_id, row, task_cnt, max_capacity, should_repaint):
    """Scroll one line down with improved edge case handling"""
    # Don't do anything if we're already at the last task
    if current_id == task_cnt:
        return start, end, current_id, row, False
        
    # Move selection down one task
    current_id += 1
    
    # Handle scrolling if needed
    if task_cnt > max_capacity and row == max_capacity:
        # We need to scroll the view down
        start = start + 1
        end = end + 1
    else:
        # Just move the highlight down
        row = row + 1
    
    # Double-check that everything is in bounds after scrolling
    if end > task_cnt:
        end = task_cnt
        start = max(1, end - max_capacity + 1)
        
    # Make sure row is consistent with current_id and start
    row = current_id - start + 1
    
    return start, end, current_id, row, should_repaint
                
def keyup_update(start, end, current_id, row, task_cnt, max_capacity, should_repaint):
    """Scroll one line up with improved edge case handling"""
    # Don't do anything if we're already at the first task
    if current_id == 1:
        return start, end, current_id, row, False
        
    # Move selection up one task
    current_id -= 1
    
    # Handle scrolling if needed
    if task_cnt >= max_capacity and start > 1 and row == 1:
        # We need to scroll the view up
        start = start - 1
        end = end - 1
    else:
        # Just move the highlight up
        row = row - 1
    
    # Double-check that everything is in bounds after scrolling
    if start < 1:
        start = 1
        end = min(start + max_capacity - 1, task_cnt)
        
    # Make sure row is consistent with current_id and start
    row = current_id - start + 1
    
    return start, end, current_id, row, should_repaint


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
               └───────┘               └───────┘               │       │               │       │
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

def is_view_fully_packed(start, end, capacity):
    """indicates whether the current view is completely filled with tasks"""
    return end - start + 1 >= capacity