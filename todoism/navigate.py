import todoism.state as st

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

def keydown_update(should_repaint):
    """Scroll one line down with improved edge case handling"""
    # Don't do anything if we're already at the last task
    if st.current_task_id == st.task_cnt:
        return False
        
    # Move selection down one task
    st.current_task_id += 1
    
    # Handle scrolling if needed
    if st.task_cnt > st.latest_max_capacity and st.current_task_row == st.latest_max_capacity:
        # We need to scroll the view down
        st.start_task_id += 1
        st.end_task_id += 1
    else:
        # Just move the highlight down
        st.current_task_row += 1
    
    # Double-check that everything is in bounds after scrolling
    if st.end_task_id > st.task_cnt:
        st.end_task_id = st.task_cnt
        st.start_task_id = max(1, st.end_task_id - st.latest_max_capacity + 1)
        
    # Make sure row is consistent with current_task_id and start
    st.current_task_row = st.current_task_id - st.start_task_id + 1
    
    return should_repaint
                
def keyup_update(should_repaint):
    """Scroll one line up with improved edge case handling"""
    # Don't do anything if we're already at the first task
    if st.current_task_id == 1:
        return False
        
    # Move selection up one task
    st.current_task_id -= 1
    
    # Handle scrolling if needed
    if st.task_cnt >= st.latest_max_capacity and st.start_task_id > 1 and st.current_task_row == 1:
        # We need to scroll the view up
        st.start_task_id = st.start_task_id - 1
        st.end_task_id = st.end_task_id - 1
    else:
        # Just move the highlight up
        st.current_task_row = st.current_task_row - 1
    
    # Double-check that everything is in bounds after scrolling
    if st.start_task_id < 1:
        st.start_task_id = 1
        st.end_task_id = min(st.start_task_id + st.latest_max_capacity - 1, st.task_cnt)
        
    # Make sure row is consistent with current_task_id and start
    st.current_task_row =  st.current_task_id - st.start_task_id + 1
    
    return should_repaint


def post_deletion_update(prev_task_cnt):
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
    if _is_view_fully_packed():
        # Senarios 1
        if prev_task_cnt == st.latest_max_capacity:
            # delete the last task, otherwise the row and id both remains unchanged
            if st.current_task_id == st.end_task_id:
                st.current_task_row = st.current_task_row - 1
                st.current_task_id = st.current_task_id - 1
            st.end_task_id = st.end_task_id - 1
        # Senario 2
        elif prev_task_cnt == st.end_task_id and prev_task_cnt > st.latest_max_capacity:
            st.start_task_id = st.start_task_id - 1
            st.end_task_id = st.end_task_id - 1
            st.current_task_id = st.current_task_id - 1
        # Senario 3 and 4 does not lead to any change
    
    # Senario 5
    else:
        st.end_task_id = st.end_task_id - 1
        if st.current_task_id == prev_task_cnt:
            st.current_task_row = st.current_task_row - 1
            st.current_task_id = st.current_task_id - 1

def _is_view_fully_packed():
    """indicates whether the current view is completely filled with tasks"""
    return st.end_task_id - st.start_task_id + 1 >= st.latest_max_capacity