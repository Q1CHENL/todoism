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