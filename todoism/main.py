import time
import curses
import todoism.utils as ut
import todoism.task as tsk
import todoism.print as pr
import todoism.settings as st
import todoism.command as cmd
import todoism.cli as cli
import todoism.category as cat
import todoism.app as app
import todoism.scroll as scr
from datetime import datetime

def main(stdscr):
    stdscr.keypad(True)  # enable e.g arrow keys
    stdscr.scrollok(True)
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()
    
    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    
    # Initialize color pairs
    curses.start_color()
    # progress colors
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    # regular color pair
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # Green for done symbol
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # Orange (using yellow as closest match) for flag symbol
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    # Set up the screen
    curses.curs_set(0)
    stdscr.clear()
    # Assuming color pair 0 represents the default colors
    stdscr.bkgd(' ', curses.COLOR_BLACK | curses.A_NORMAL)

    # Define the initial todo list
    task_list = tsk.load_tasks()
    # Update existing tasks to include category_id if missing
    task_list = tsk.update_existing_tasks()
    
    # Load categories
    categories = cat.load_categories()
    
    # Initialize focus manager
    focus_manager = app.FocusManager()
    
    # Initialize category state
    current_category_id = 0  # Start with "All" category
    
    done_list = []  # a part of task list
    purged_list = []

    ut.reid(task_list)  # reid in case something went wrong in last session
    
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()
    # Subtract 2 instead of 1 (1 for status bar + 1 for bottom frame)
    max_capacity = max_y - 2
    
    # Initialize sidebar scroller
    sidebar_scroller = app.SidebarScroller(len(categories), max_capacity)
    
    # Get filtered task list for current category
    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
    
    # Initialize task display state
    task_cnt = len(filtered_tasks)  # done + undone
    done_cnt = tsk.done_count(filtered_tasks)
    current_id = 1 if task_cnt > 0 else 0  # id of task selected
    current_row = 1 if task_cnt > 0 else 0  # range: [0, height-1]
    
    # Initialize task scrolling (using the original logic)
    start = 1 if task_cnt > 0 else 0
    end = task_cnt if task_cnt < max_capacity else max_capacity
    
    should_repaint = True
    
    # Set a timeout for getch() to make it non-blocking (500ms)
    stdscr.timeout(500)
    # Track when we last updated the time
    last_time_update = time.time()
    
    # Initialize key to avoid UnboundLocalError
    key = 0
    
    # Sidebar width
    sidebar_width = 16  # 15 for sidebar + 1 for separator
    
    while True:
        # Get filtered tasks for current category
        filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
        task_cnt = len(filtered_tasks)
        done_cnt = tsk.done_count(filtered_tasks)
        
        # Get current window dimensions
        new_max_y, max_x = stdscr.getmaxyx()
        new_max_capacity = new_max_y - 2  # Account for status bar
        
        # Check if window height has changed and we need to adjust view
        if new_max_capacity != max_capacity:
            # Store if we're getting more or less space
            is_growing = new_max_capacity > max_capacity
            old_capacity = max_capacity
            max_capacity = new_max_capacity
            
            # Update sidebar scroller with new visible height
            sidebar_scroller.update_visible_height(max_capacity)
            
            # For tasks, use improved resize logic
            if task_cnt > 0:
                if is_growing:
                    # WINDOW GROWING: Show maximum possible tasks while keeping current selection visible

                    # Calculate how much more space we have
                    extra_capacity = max_capacity - old_capacity

                    # Step 1: First attempt to fill from bottom
                    # Calculate how many more tasks we could show with new size
                    potential_end = min(task_cnt, start + max_capacity - 1)

                    # Step 2: If we still have space after showing more at bottom, 
                    # show more at top too (if possible)
                    if potential_end - start + 1 < max_capacity and start > 1:
                        # Calculate how much space is still available after filling bottom
                        remaining_space = max_capacity - (potential_end - start + 1)

                        # Fill from top with remaining space
                        new_start = max(1, start - remaining_space)

                        # Update start and end
                        start = new_start
                        end = min(task_cnt, start + max_capacity - 1)
                    else:
                        # Just extend end as much as possible
                        end = potential_end

                    # Step 3: Special case for when we're near the end of the list
                    # If we're not showing the maximum possible tasks, pull the window up
                    visible_count = end - start + 1
                    if visible_count < max_capacity and end < task_cnt:
                        # We have empty space but more tasks below - adjust both ends
                        end = min(task_cnt, end + (max_capacity - visible_count))
                        visible_count = end - start + 1

                        if visible_count < max_capacity and start > 1:
                            # Still have space? Pull up from top too
                            spaces_to_fill = max_capacity - visible_count
                            start = max(1, start - spaces_to_fill)
                            end = min(task_cnt, start + max_capacity - 1)

                    # Step 4: Special case when we're at the end of the list
                    # If end is at max and we have space, pull window up
                    if end == task_cnt and end - start + 1 < max_capacity and start > 1:
                        # Calculate how many more items we could show at top
                        available_slots = max_capacity - (end - start + 1)
                        new_start = max(1, start - available_slots)
                        start = new_start

                    # Make sure current task stays visible by adjusting view if needed
                    if current_id < start:
                        # If current task would be above visible area, adjust view
                        start = current_id
                        end = min(task_cnt, start + max_capacity - 1)
                    elif current_id > end:
                        # If current task would be below visible area, adjust view
                        end = current_id
                        start = max(1, end - max_capacity + 1)

                    # Update current_row based on adjusted start/end
                    current_row = current_id - start + 1
                else:
                    # WINDOW SHRINKING: Keep current task visible but reduce what's shown
                    # Make sure end doesn't exceed capacity from start
                    if end > start + max_capacity - 1:
                        end = start + max_capacity - 1
                        
                    # If end exceeds task count, adjust both end and start
                    if end > task_cnt:
                        end = task_cnt
                        start = max(1, end - max_capacity + 1)
                        
                    # Make sure current task is still visible by adjusting start if needed
                    if current_id < start:
                        start = current_id
                        end = min(start + max_capacity - 1, task_cnt)
                    elif current_id > end:
                        end = current_id
                        start = max(1, end - max_capacity + 1)
            
            # Force a repaint after window resize
            should_repaint = True
            
            # Ensure separator is visible after resize
            pr.ensure_separator_visible(stdscr, new_max_y)
        
        # Check if we need to update the time (every second)
        current_time = time.time()
        if current_time - last_time_update >= 2.0:  # Increased to 2 seconds to reduce lag
            pr.print_status_bar(stdscr, done_cnt, task_cnt)
            stdscr.refresh()
            last_time_update = current_time
            
        # Selected task highlighting
        if should_repaint:
            stdscr.erase()
            color_selected = st.get_color_selected()
            curses.init_pair(1, curses.COLOR_BLACK, color_selected)
            
            if focus_manager.is_tasks_focused():
                # Update task view using existing scrolling logic
                if task_cnt > 0:
                    # Ensure valid current_id
                    if current_id > task_cnt:
                        current_id = task_cnt
                        current_row = min(current_row, max_capacity)
                    
                    # Render the main view with sidebar
                    pr.print_main_view_with_sidebar(
                        stdscr,
                        done_cnt,
                        task_cnt,
                        filtered_tasks,
                        current_id,
                        start,
                        end,
                        categories,
                        current_category_id,
                        sidebar_scroller.start_index,
                        False  # Sidebar does not have focus
                    )
                else:
                    # No tasks in current category
                    pr.print_status_bar(stdscr, done_cnt, task_cnt)
                    pr.print_sidebar(
                        stdscr,
                        categories,
                        current_category_id,
                        sidebar_scroller.start_index,
                        max_capacity,
                        False  # Sidebar does not have focus
                    )
                    pr.print_msg(stdscr, pr.empty_msg, 16, True)  # Add highlight=True to highlight message when task panel has focus
            else:
                # Focus on sidebar - don't highlight any task
                pr.print_main_view_with_sidebar(
                    stdscr,
                    done_cnt,
                    task_cnt,
                    filtered_tasks,
                    0,  # Pass 0 to indicate no task should be highlighted
                    start,
                    end,
                    categories,
                    current_category_id,
                    sidebar_scroller.start_index,
                    True  # Sidebar has focus
                )

            should_repaint = False
            
        # Wait for user input
        key = stdscr.getch()
        
        if key == -1:
            continue
            
        # Handle Tab key to switch focus
        if key == 9:  # Tab key
            focus_manager.toggle_focus()
            should_repaint = True
            continue
            
        # Handle mouse events
        if key == curses.KEY_MOUSE:
            try:
                mouse_id, mouse_x, mouse_y, mouse_z, button_state = curses.getmouse()
                
                # Check if clicked in sidebar area
                if mouse_x < sidebar_width:
                    if 1 <= mouse_y <= min(len(categories), max_capacity):
                        # Calculate the category ID that was clicked
                        clicked_cat_index = sidebar_scroller.start_index + mouse_y - 1
                        
                        if 0 <= clicked_cat_index < len(categories):
                            # Set focus to sidebar if not already
                            if not focus_manager.is_sidebar_focused():
                                focus_manager.toggle_focus()
                                
                            # Update the selected category
                            sidebar_scroller.current_index = clicked_cat_index
                            current_category_id = categories[clicked_cat_index]['id']
                            
                            # Reset task selection for the new category
                            filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                            task_cnt = len(filtered_tasks)
                            current_id = 1 if task_cnt > 0 else 0
                            current_row = 1 if task_cnt > 0 else 0
                            start = 1 if task_cnt > 0 else 0
                            end = task_cnt if task_cnt < max_capacity else max_capacity
                            
                            should_repaint = True
                    continue
                
                # Handle clicks in task area
                # Check if clicked on a task row (rows start at 1, status bar is at row 0)
                if 1 <= mouse_y <= min(task_cnt, max_capacity):
                    # Set focus to tasks if not already
                    if not focus_manager.is_tasks_focused():
                        focus_manager.toggle_focus()
                        
                    # Calculate the display position clicked (this is now the same as the display ID)
                    clicked_display_position = start + mouse_y - 1
                    
                    # Get the visual row that was clicked
                    clicked_task_row = mouse_y  # Row on screen
                    
                    # Map this to actual task in filtered_tasks
                    if start <= clicked_display_position <= end and clicked_display_position - start < len(filtered_tasks):
                        task_index = clicked_display_position - 1  # Adjust to 0-based index for array
                        
                        # Define click regions - adjusted for sidebar offset
                        status_x_start = sidebar_width + 3
                        status_x_end = sidebar_width + 4  # Status symbol 
                        flag_x_start = sidebar_width + 5
                        flag_x_end = sidebar_width + 6    # Flag symbol
                        
                        # Check if clicked on status symbol (✓)
                        if status_x_start <= mouse_x <= status_x_end:
                            # Toggle task status (done/undone)
                            if filtered_tasks:
                                done_list.append(filtered_tasks[task_index])
                                filtered_tasks[task_index]['status'] = not filtered_tasks[task_index]['status']
                                tsk.save_tasks(task_list, tsk.tasks_file_path)
                                should_repaint = True
                        
                        # Check if clicked on flag symbol (⚑)
                        elif flag_x_start <= mouse_x <= flag_x_end:
                            # Toggle task flag
                            if filtered_tasks:
                                filtered_tasks[task_index]['flagged'] = not filtered_tasks[task_index]['flagged']
                                tsk.save_tasks(task_list, tsk.tasks_file_path)
                                should_repaint = True
                        
                        # Otherwise, just select the task
                        else:
                            # Update current selection - the current_id is now a display position
                            current_id = clicked_display_position
                            current_row = clicked_task_row
                            should_repaint = True
            except curses.error:
                # getmouse() can raise an exception if the terminal doesn't support mouse
                pass
            
        # Handle sidebar navigation when sidebar is focused
        elif focus_manager.is_sidebar_focused():
            if key == curses.KEY_UP:
                sidebar_scroller.scroll_up()
                # Update current_category_id based on current_index
                if len(categories) > 0:
                    current_category_id = categories[sidebar_scroller.current_index]['id']
                    
                    # Reset task selection for the new category
                    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                    task_cnt = len(filtered_tasks)
                    current_id = 1 if task_cnt > 0 else 0
                    current_row = 1 if task_cnt > 0 else 0
                    start = 1 if task_cnt > 0 else 0
                    end = task_cnt if task_cnt < max_capacity else max_capacity
                    
                should_repaint = True
                
            elif key == curses.KEY_DOWN:
                sidebar_scroller.scroll_down()
                # Update current_category_id based on current_index
                if len(categories) > 0:
                    current_category_id = categories[sidebar_scroller.current_index]['id']
                    
                    # Reset task selection for the new category
                    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                    task_cnt = len(filtered_tasks)
                    current_id = 1 if task_cnt > 0 else 0
                    current_row = 1 if task_cnt > 0 else 0
                    start = 1 if task_cnt > 0 else 0
                    end = task_cnt if task_cnt < max_capacity else max_capacity
                    
                should_repaint = True
            
            # Add quit functionality 
            elif key == ord('q'):
                break
                
            # Add key handlers for categories - just like tasks
            elif key == ord('a'):
                # Add a new category with live preview
                curses.echo()
                curses.curs_set(1)
                
                # Calculate the position where new category would appear
                cat_count = len(categories)
                visible_count = min(cat_count, max_capacity)
                new_cat_row = visible_count + 1  # Row after last visible category
                
                # If we're at max capacity, use the last line
                if new_cat_row > max_capacity:
                    new_cat_row = max_capacity
                
                # Calculate new category ID
                new_cat_id = max([c['id'] for c in categories], default=0) + 1
                
                # Create a temporary category for editing
                temp_category = {
                    'id': new_cat_id, 
                    'name': '',
                    'color': 'blue',
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                # DON'T erase the entire screen - save the current screen content
                stdscr.refresh()
                
                # Redraw status bar first (always needed)
                pr.print_status_bar(stdscr, done_cnt, task_cnt)
                
                # Only clear and redraw the SIDEBAR PORTION of each line (columns 0-14)
                # This preserves tasks on the same lines
                for i in range(0, max_capacity + 1):
                    # Clear only the sidebar portion of each line (not the entire line)
                    for j in range(15):  # Clear only columns 0-14
                        stdscr.addch(i, j, ' ')
                    
                    # Restore the separator line
                    stdscr.addch(i, 15, '│')
                
                # Redraw all categories in the sidebar
                pr.print_sidebar(
                    stdscr,
                    categories,
                    current_category_id,
                    sidebar_scroller.start_index,
                    max_capacity,
                    True  # Sidebar has focus
                )
                stdscr.refresh()

                # Redraw all tasks to ensure they're visible
                if task_cnt > 0:
                    pr.print_tasks_with_offset(stdscr, filtered_tasks, 0, start, end, sidebar_width)
                else:
                    pr.print_msg(stdscr, pr.empty_msg, sidebar_width)
                
                # Print new category placeholder
                stdscr.addstr(new_cat_row, 0, f"{new_cat_id:2d} ")
                
                # Move cursor to the consistent 1-space indent position
                stdscr.move(new_cat_row, 1)  # 1-space indent, matching print_category()
                stdscr.refresh()
                
                # Use the same edit function as for tasks, but adapt for sidebar position
                temp_category['description'] = ''  # Add this field for edit function compatibility
                new_cat_name = ut.edit(stdscr, temp_category, pr.add_mode, 0, 0, is_sidebar=True)
                temp_category['name'] = new_cat_name  # Store result in name field
                
                if new_cat_name:
                    # Enforce maximum length for category name
                    if len(new_cat_name) > cat.MAX_CATEGORY_NAME_LENGTH:
                        new_cat_name = new_cat_name[:cat.MAX_CATEGORY_NAME_LENGTH]
                        
                    # Add the category
                    new_cat = cat.add_category(new_cat_name)
                    if new_cat:
                        # Reload categories and update scroller
                        categories = cat.load_categories()
                        sidebar_scroller.update_total(len(categories))
                        
                        # Find and select the new category
                        for i, c in enumerate(categories):
                            if c['id'] == new_cat['id']:
                                sidebar_scroller.current_index = i
                                current_category_id = new_cat['id']
                                break
                                
                        # Update filtered tasks for the new category
                        filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                        task_cnt = len(filtered_tasks)
                        current_id = 1 if task_cnt > 0 else 0
                        current_row = 1 if task_cnt > 0 else 0
                        start = 1 if task_cnt > 0 else 0
                        end = task_cnt if task_cnt < max_capacity else max_capacity
                
                curses.curs_set(0)
                curses.noecho()
                should_repaint = True
                
            elif key == ord('e'):
                # Edit category name with scrolling (skip for "All" category)
                if len(categories) > 0 and current_category_id != 0:
                    curses.echo()
                    curses.curs_set(1)
                    
                    # Get current category to edit
                    current_cat = categories[sidebar_scroller.current_index]
                    row = sidebar_scroller.current_index - sidebar_scroller.start_index + 1
                    
                    # Clear and redraw to show edit mode
                    stdscr.erase()
                    pr.print_status_bar(stdscr, done_cnt, task_cnt)
                    
                    # Draw all categories
                    pr.print_sidebar(
                        stdscr,
                        categories,
                        current_category_id,
                        sidebar_scroller.start_index,
                        max_capacity,
                        True
                    )
                    
                    # Draw tasks area
                    pr.print_tasks_with_offset(stdscr, filtered_tasks, 0, start, end, sidebar_width)
                    
                    # Highlight ONLY THE SIDEBAR PORTION of the category being edited
                    stdscr.attron(curses.color_pair(1))
                    stdscr.move(row, 0)
                    
                    # FIXED: Don't use clrtoeol() - instead clear only the sidebar area
                    for j in range(15):  # Clear only the sidebar width
                        stdscr.addch(row, j, ' ')
                        
                    # Redraw the separator
                    stdscr.attroff(curses.color_pair(1))
                    stdscr.addstr(row, 15, '│')
                    
                    # Position cursor at start of category name (1-space indent)
                    stdscr.move(row, 1)
                    stdscr.refresh()
                    
                    # Create a temporary copy for editing using the same mechanism as tasks
                    edit_cat = current_cat.copy()
                    edit_cat['description'] = current_cat['name']  # Map name to description for edit function
                    
                    # Use the edit function with the same scrolling capabilities
                    # MODIFIED LINE BELOW: Set initial cursor position to the end of the name
                    new_name = ut.edit(stdscr, edit_cat, pr.edit_mode, 0, len(current_cat['name']), is_sidebar=True)
                    
                    if new_name:
                        # Enforce maximum length for category name
                        if len(new_name) > cat.MAX_CATEGORY_NAME_LENGTH:
                            new_name = new_name[:cat.MAX_CATEGORY_NAME_LENGTH]
                            
                        # Update the name
                        cat.update_category_name(current_category_id, new_name)
                        
                        # Reload categories
                        categories = cat.load_categories()
                    
                    # ADDED: Restore task display after editing
                    pr.print_tasks_with_offset(stdscr, filtered_tasks, current_id, start, end, sidebar_width)
                    
                    curses.curs_set(0)
                    curses.noecho()
                    should_repaint = True
            
            elif key == curses.KEY_BACKSPACE or key == 127:
                # Delete selected category (with double backspace confirmation)
                if len(categories) > 0 and current_category_id != 0:  # Don't delete "All"
                    # Wait for second backspace
                    stdscr.addstr(max_capacity, sidebar_width, "Press backspace again to delete")
                    stdscr.refresh()
                    
                    # Wait for confirmation
                    k = stdscr.getch()
                    if k == curses.KEY_BACKSPACE or k == 127:
                        # Remember current position in the list
                        current_index = sidebar_scroller.current_index
                        
                        # Handle tasks in this category - REMOVE instead of moving to "All"
                        task_list = [task for task in task_list if task.get('category_id', 0) != current_category_id]

                        # Renumber all tasks
                        ut.reid(task_list)

                        # Save tasks
                        tsk.save_tasks(task_list, tsk.tasks_file_path)
                        
                        # Delete the category
                        cat.delete_category(current_category_id)
                        
                        # Renumber all categories to maintain sequential IDs
                        categories = cat.reassign_category_ids()
                        
                        # Update task category references to match new category IDs
                        # This is only necessary if we're renumbering categories
                        if len(categories) > 1:
                            # We need to reload tasks after renumbering to ensure proper associations
                            task_list = tsk.load_tasks()
                        
                        # Update sidebar scroller with new category count
                        sidebar_scroller.update_total(len(categories))
                        
                        # Select appropriate category after deletion
                        if len(categories) > 1:  # If we have categories beyond just "All"
                            # Always select the last non-All category after deletion
                            new_index = len(categories) - 1
                            sidebar_scroller.current_index = new_index
                            current_category_id = categories[new_index]['id']
                        else:
                            # If only "All" remains, select it
                            sidebar_scroller.current_index = 0
                            current_category_id = 0
                        
                        # Reset filtered tasks
                        filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                        task_cnt = len(filtered_tasks)
                        
                        # Reset task selection using original logic
                        current_id = 1 if task_cnt > 0 else 0
                        current_row = 1 if task_cnt > 0 else 0
                        start = 1 if task_cnt > 0 else 0
                        end = task_cnt if task_cnt < max_capacity else max_capacity
                    
                    # Clear the status line
                    stdscr.move(max_capacity, 0)
                    stdscr.clrtoeol()
                    should_repaint = True
                
        # Handle task navigation and actions when task area is focused
        elif focus_manager.is_tasks_focused():
            # Handle user input for tasks
            if key == ord('a'):
                # Allow task creation in "All" category
                if task_cnt == ut.max_task_count:
                    pr.print_msg(stdscr, pr.limit_msg)
                    stdscr.refresh()
                    time.sleep(1.2)
                    continue
                
                # Rest of the task addition code continues...
                curses.echo()
                curses.curs_set(1)
                
                # Store old values for potential rollback
                old_start = start
                old_end = end
                
                # adjust start end for pre-print
                # taskoverflow if a new one is added:
                if task_cnt >= max_capacity:
                    if end <= task_cnt:
                        start = task_cnt - (end - start - 1)
                        end = task_cnt
                        
                # DO NOT use erase() as it clears everything
                # Instead, only clear the task area while preserving sidebar
                stdscr.erase()  # We'll redraw everything properly
                pr.print_status_bar(stdscr, done_cnt, task_cnt)

                # Draw sidebar
                pr.print_sidebar(
                    stdscr,
                    categories,
                    current_category_id,
                    sidebar_scroller.start_index,
                    max_capacity,
                    False
                )

                # Print existing tasks with offset (crucial: pass sidebar_width to offset tasks)
                pr.print_tasks_with_offset(stdscr, filtered_tasks, 0, start, end, sidebar_width)

                # Add a new task with proper indentation
                new_task_num = f"{task_cnt + 1:2d}"
                y_pos = max_capacity if task_cnt >= max_capacity else task_cnt + 1
                stdscr.addstr(y_pos, sidebar_width, f"{new_task_num} ")

                # Move cursor to the correct position after task number
                stdscr.move(y_pos, sidebar_width + ut.indent)
                stdscr.refresh()

                # Add a new task
                new_task = tsk.create_new_task(task_cnt + 1)
                
                # Set category_id to 0 if in "All" category, otherwise use current category
                new_task['category_id'] = 0 if current_category_id == 0 else current_category_id
                
                new_task_description = ut.edit(stdscr, new_task, pr.add_mode)
                
                if new_task_description != "":
                    new_id = task_cnt + 1
                    task_list = tsk.add_new_task(
                        task_list, new_id, new_task_description, False, new_task['category_id'])
                    task_cnt = task_cnt + 1
                    
                    # Update filtered tasks
                    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                    
                    if task_cnt == 1:
                        start = 1
                    if task_cnt - 1 <= max_capacity:
                        current_row = task_cnt
                    else:
                        current_row = max_capacity
                    current_id = new_id  # new id
                    end = end + 1  # change end as well
                else:
                    # User cancelled adding a new task
                    start = old_start
                    end = old_end
                    # Force full repaint to clear the empty task line
                    should_repaint = True
                    # Continue to next iteration without adding a task
                    curses.curs_set(0)
                    curses.noecho()
                    continue
                    
                # Redraw with updated task list
                pr.print_tasks_with_offset(stdscr, filtered_tasks, current_id, start, end, sidebar_width)
                stdscr.refresh()
                curses.curs_set(0)
                curses.noecho()
                
            elif key == ord('d') or key == ord(' '):
                # mark the current task as 'done'
                if filtered_tasks and current_id > 0:
                    task_idx = current_id - 1
                    done_list.append(filtered_tasks[task_idx])
                    filtered_tasks[task_idx]['status'] = not filtered_tasks[task_idx]['status']
                    tsk.save_tasks(task_list, tsk.tasks_file_path)
                    should_repaint = True
                    
            elif key == ord('e'):
                curses.echo()
                curses.curs_set(1)
                if task_cnt > 0 and current_id > 0:
                    task_idx = current_id - 1
                    
                    # Override the current task row y-position to account for sidebar
                    edit_row = current_row  # Row is correct, it's relative to visible area
                    
                    # Get the task's description length and add offset for sidebar
                    desc_length = len(filtered_tasks[task_idx]['description']) + ut.indent
                    
                    # Call edit_and_save with adjusted parameters for sidebar offset
                    stdscr.erase()
                    pr.print_status_bar(stdscr, done_cnt, task_cnt)
                    
                    # Display sidebar
                    pr.print_sidebar(
                        stdscr,
                        categories,
                        current_category_id,
                        sidebar_scroller.start_index,
                        max_capacity,
                        False
                    )
                    
                    # Render all tasks with offset
                    pr.print_tasks_with_offset(stdscr, filtered_tasks, current_id, start, end, sidebar_width)
                    
                    # Move cursor to edit position
                    stdscr.move(edit_row, sidebar_width + ut.indent)
                    stdscr.refresh()
                    
                    # Use regular edit, but with the task offset in the interface
                    filtered_tasks[task_idx]['description'] = ut.edit(
                        stdscr, 
                        filtered_tasks[task_idx], 
                        pr.edit_mode
                    )
                    
                    # Handle task deletion if description is empty
                    if filtered_tasks[task_idx]['description'] == "":
                        # Find and delete the task
                        for i, task in enumerate(task_list):
                            if task['id'] == filtered_tasks[task_idx]['id']:
                                del task_list[i]
                                break
                        
                        # Update IDs
                        ut.reid(task_list)
                        
                        # Update filtered tasks and counts
                        filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                        task_cnt = len(filtered_tasks)
                        
                        # Adjust selection after deletion
                        if task_cnt == 0:
                            current_id = 0
                            current_row = 0
                            start = 0
                            end = 0
                            # Clear task area and show empty message
                            for i in range(1, max_capacity + 1):
                                stdscr.move(i, sidebar_width)
                                stdscr.clrtoeol()
                            pr.print_msg(stdscr, pr.empty_msg)
                        else:
                            # Keep the same visual position if possible
                            if current_id > task_cnt:
                                current_id = task_cnt
                            
                            # Adjust scroll range
                            if end > task_cnt:
                                end = task_cnt
                                start = max(1, end - max_capacity + 1)
                            
                            # Update current row
                            current_row = current_id - start + 1
                            
                            # Start redraw from one row above the deleted position
                            start_redraw = max(1, current_row - 1)
                            
                            # Update tasks from one row above deletion
                            for i in range(start_redraw, min(task_cnt - start + 2, max_capacity + 1)):
                                y = i
                                task_index = start + i - 1
                                
                                # Clear just this line
                                stdscr.move(y, sidebar_width)
                                stdscr.clrtoeol()
                                
                                # Render the task if it exists
                                if task_index < task_cnt:
                                    pr.render_task(
                                        stdscr,
                                        filtered_tasks[task_index],
                                        y,
                                        task_index + 1 == current_id,
                                        max_x=max_x
                                    )
                            
                            # Clear the last line if needed
                            if task_cnt - start + 1 < max_capacity:
                                stdscr.move(task_cnt - start + 2, sidebar_width)
                                stdscr.clrtoeol()
                        
                        # Update status bar and refresh
                        pr.print_status_bar(stdscr, done_cnt, task_cnt)
                        stdscr.refresh()
                    
                    # Save changes
                    tsk.save_tasks(task_list, tsk.tasks_file_path)
                    should_repaint = True
                    
                curses.curs_set(0)
                curses.noecho()
                
            elif key == ord('f'):
                if filtered_tasks and current_id > 0:
                    task_idx = current_id - 1
                    filtered_tasks[task_idx]['flagged'] = not filtered_tasks[task_idx]['flagged']
                    tsk.save_tasks(task_list, tsk.tasks_file_path)
                    should_repaint = True
                
            elif key == ord('q'):
                break
                
            elif key == ord(':'):
                curses.echo()
                curses.curs_set(1)
                
                # Disable timeout temporarily
                stdscr.timeout(-1)
                
                # Place the command input at the bottom of the screen, after the sidebar
                stdscr.addstr(max_capacity, sidebar_width, ":")
                stdscr.refresh()
                
                # Get command input
                command_line = stdscr.getstr().decode('utf-8')
                
                # Restore timeout
                stdscr.timeout(500)
                
                curses.curs_set(0)
                curses.noecho()
                
                # Process regular commands
                task_list, done_list, current_id, current_row, start, end = cmd.execute_command(
                    stdscr,
                    command_line,
                    task_list,
                    done_list,
                    purged_list,
                    current_id,
                    start,
                    end,
                    current_row,
                    max_capacity
                )
                
                # Process category-specific commands
                if command_line.startswith("c"):
                    categories, current_category_id = cmd.execute_category_command(
                        stdscr,
                        command_line,
                        categories,
                        task_list,
                        current_category_id
                    )
                    
                    # Update sidebar scroller
                    sidebar_scroller.update_total(len(categories))
                    
                    # Find the index of the selected category
                    for i, c in enumerate(categories):
                        if c['id'] == current_category_id:
                            sidebar_scroller.current_index = i
                            break
                    
                    # Update filtered tasks
                    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                    task_cnt = len(filtered_tasks)
                    
                    # Reset task selection using original logic
                    if task_cnt > 0:
                        current_id = 1
                        current_row = 1
                        start = 1
                        end = min(max_capacity, task_cnt)
                    else:
                        current_id = 0
                        current_row = 0
                        start = 0
                        end = 0
                
                should_repaint = True
                
                # Clear command line
                command_line = ""
                
            elif key == curses.KEY_UP:
                if task_cnt > 0:
                    # Use original keyup logic
                    start, end, current_id, current_row, should_repaint = scr.keyup_update(
                        start, end, current_id, current_row, task_cnt, max_capacity, True
                    )
                
            elif key == curses.KEY_DOWN:
                if task_cnt > 0:
                    # Use original keydown logic
                    start, end, current_id, current_row, should_repaint = scr.keydown_update(
                        start, end, current_id, current_row, task_cnt, max_capacity, True
                    )
                
            elif key == curses.KEY_BACKSPACE or key == 127:
                # Double backspace to delete a task
                k = stdscr.getch()
                if k == curses.KEY_BACKSPACE or k == 127:
                # only perform deletion when task_cnt > 0
                    if task_cnt > 0:
                        # update done_cnt
                        if task_list[current_id - 1]['status'] is True:
                            done_cnt = done_cnt - 1
                        # perform deletion
                        del task_list[current_id - 1]
                        # reid
                        ut.reid(task_list)
                        # view change rules are similar to apple reminder
                        current_id, current_row, start, end = ut.post_deletion_update(
                            current_id,
                            current_row,
                            start,
                            end,
                            task_cnt,
                            max_capacity
                        )

                        # update task_cnt
                        task_cnt = task_cnt - 1
                    tsk.save_tasks(task_list, tsk.tasks_file_path)
                    should_repaint = True


def run():
    args = cli.parse_args()
    if args.add:
        tsk.add_new_task_cli(args.add, args.flag)
    elif args.delete:
        tsk.remove_task_cli(args.delete)
    elif args.print_all:
        todos = tsk.load_tasks()
        pr.print_all_cli(todos)
    elif args.version:
        pr.print_version()
    else:
        curses.wrapper(main)


if __name__ == "__main__":
    run()
