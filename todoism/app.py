import curses
import todoism.task as tsk
import todoism.category as cat
import todoism.print as pr
import todoism.command as cmd
import todoism.edit as ed

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