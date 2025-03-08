class FocusManager:
    """Manages focus between sidebar and task list"""
    SIDEBAR = 0
    TASKS = 1
    
    def __init__(self):
        self.current_focus = self.TASKS
    
    def toggle_focus(self):
        """Switch focus between sidebar and tasks"""
        self.current_focus = self.SIDEBAR if self.current_focus == self.TASKS else self.TASKS
        
    def is_sidebar_focused(self):
        """Check if sidebar has focus"""
        return self.current_focus == self.SIDEBAR
        
    def is_tasks_focused(self):
        """Check if task list has focus"""
        return self.current_focus == self.TASKS

class SidebarScroller:
    """Manages scrolling for sidebar categories"""
    def __init__(self, total_items=0, visible_height=10):
        self.start_index = 0
        self.total_items = total_items
        self.visible_height = visible_height
        self.current_index = 0
        
    def scroll_up(self):
        """Move selection up one item"""
        if self.current_index > 0:
            self.current_index -= 1
            # Scroll view if needed
            if self.current_index < self.start_index:
                self.start_index = self.current_index
        return self.current_index, self.start_index
        
    def scroll_down(self):
        """Move selection down one item"""
        if self.current_index < self.total_items - 1:
            self.current_index += 1
            # Scroll view if needed
            if self.current_index >= self.start_index + self.visible_height:
                self.start_index += 1
        return self.current_index, self.start_index
                
    def update_total(self, new_total):
        """Update the total number of items"""
        self.total_items = new_total
        # Adjust current index if it would be out of bounds
        if self.current_index >= self.total_items and self.total_items > 0:
            self.current_index = self.total_items - 1
        # Adjust start index if needed
        if self.start_index + self.visible_height > self.total_items:
            self.start_index = max(0, self.total_items - self.visible_height)
        return self.current_index, self.start_index
            
    def update_visible_height(self, new_height):
        """Update the number of visible items"""
        self.visible_height = new_height
        # Adjust start index if needed
        if self.start_index + self.visible_height > self.total_items:
            self.start_index = max(0, self.total_items - self.visible_height)
        return self.start_index

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