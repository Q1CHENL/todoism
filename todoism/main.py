import time
import uuid
import curses
import todoism.edit as ed
import todoism.task as tsk
import todoism.print as pr
import todoism.settings as st
import todoism.command as cmd
import todoism.cli as cli
import todoism.category as cat
import todoism.navigate as nv
from datetime import datetime

def main(stdscr):
    stdscr.keypad(True)  # enable e.g arrow keys
    stdscr.scrollok(True)
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()
    
    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    
    curses.start_color()
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
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
    focus_manager = nv.FocusManager()
    
    current_category_id = 0  # Start with "All" category
    
    done_list = []  # a part of task list
    purged_list = []

    tsk.reassign_task_ids(task_list)  # reassign_task_ids in case something went wrong in last session
    
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()
    
    max_capacity = max_y - 2 # status and bottom frame
    
    # Initialize sidebar scroller
    sidebar_scroller = nv.SidebarScroller(len(categories), max_capacity)
    
    # Get filtered task list for current category
    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
    
    # Initialize task display state
    task_cnt = len(filtered_tasks)  # done + undone
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
        
        # Handling window resizing
        new_max_y, max_x = stdscr.getmaxyx()
        new_max_capacity = new_max_y - 2
        
        # In case of window height change
        if new_max_capacity != max_capacity:
            # Store if we're getting more or less space
            is_growing = new_max_capacity > max_capacity
            old_capacity = max_capacity
            max_capacity = new_max_capacity
            
            # Update sidebar view
            sidebar_scroller.update_visible_height(max_capacity)
            
            # Update task view
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
            
        if should_repaint:
            stdscr.erase()
            color_selected = st.get_color_selected()
            curses.init_pair(1, curses.COLOR_BLACK, color_selected)
            tsk.reassign_task_ids(filtered_tasks)
            if focus_manager.is_tasks_focused():
                # Update task view using existing scrolling logic
                if task_cnt > 0:
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
                        sidebar_has_focus=False
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
                        has_focus=False
                    )
                    pr.print_msg(stdscr, pr.empty_msg, 16, highlight=True)
            else:
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
            
        if key == 9:  # Tab key for switching focus
            focus_manager.toggle_focus()
            should_repaint = True
            continue
            
        if key == curses.KEY_MOUSE:
            try:
                mouse_id, mouse_x, mouse_y, mouse_z, button_state = curses.getmouse()
                
                # Check if clicked in sidebar area (including blank areas)
                if mouse_x < sidebar_width:
                    if not focus_manager.is_sidebar_focused():
                        focus_manager.toggle_focus()
                        should_repaint = True
                    
                    # Only handle category selection if clicked on a valid category
                    if 1 <= mouse_y <= min(len(categories), max_capacity):
                        clicked_cat_index = sidebar_scroller.start_index + mouse_y - 1
                        
                        if 0 <= clicked_cat_index < len(categories):
                            old_category_id = current_category_id
                            sidebar_scroller.current_index = clicked_cat_index
                            current_category_id = categories[clicked_cat_index]['id']
                            
                            if old_category_id != current_category_id:
                                filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                                task_cnt = len(filtered_tasks)
                                current_id = 1 if task_cnt > 0 else 0
                                current_row = 1 if task_cnt > 0 else 0
                                start = 1 if task_cnt > 0 else 0
                                end = task_cnt if task_cnt < max_capacity else max_capacity
                                should_repaint = True
                    continue
                
                # Handle clicks in task area (including blank areas)
                if mouse_x >= sidebar_width:
                    if not focus_manager.is_tasks_focused():
                        focus_manager.toggle_focus()
                        should_repaint = True
                    
                    # Only handle task selection if clicked on a valid task row
                    if 1 <= mouse_y <= min(task_cnt, max_capacity):
                        clicked_task_id = start + mouse_y - 1
                        clicked_task_row = mouse_y  # Row on screen
                        
                        if start <= clicked_task_id <= end:
                            task_index = clicked_task_id - 1
                            
                            status_x_start = sidebar_width + 3
                            status_x_end = status_x_start + 1 
                            
                            flag_x_start = sidebar_width + 5
                            flag_x_end = flag_x_start + 1

                            if status_x_start <= mouse_x <= status_x_end:
                                if filtered_tasks:
                                    done_list.append(filtered_tasks[task_index])
                                    filtered_tasks[task_index]['status'] = not filtered_tasks[task_index]['status']
                                    tsk.save_tasks(task_list, tsk.tasks_file_path)
                            elif flag_x_start <= mouse_x <= flag_x_end:
                                if filtered_tasks:
                                    filtered_tasks[task_index]['flagged'] = not filtered_tasks[task_index]['flagged']
                                    tsk.save_tasks(task_list, tsk.tasks_file_path)
                            else:
                                current_id = clicked_task_id
                                current_row = clicked_task_row
                            should_repaint = True
            except curses.error:
                # getmouse() can raise an exception if the terminal doesn't support mouse
                pass
            
        elif focus_manager.is_sidebar_focused():
            if key == curses.KEY_UP:
                sidebar_scroller.scroll_up()
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
            
            elif key == ord('q'):
                # Try to restore data if in test mode, but don't fail if test module isn't available
                try:
                    import test.test as test_module
                    if test_module.is_test_mode_active():
                        test_module.restore_data()
                except ImportError:
                    # No test module found (PyPI installation), continue with normal exit
                    pass
                break
                
            elif key == ord('a'):
                curses.echo()
                curses.curs_set(1)
                
                # Calculate the position where new category would appear
                cat_count = len(categories)
                visible_count = min(cat_count, max_capacity)
                is_sidebar_full = visible_count >= max_capacity
                if is_sidebar_full:
                    # scroll up
                    sidebar_scroller.start_index += 1
                    new_cat_row = max_capacity
                else:
                    new_cat_row = visible_count + 1
                    
                new_cat_id = max([c['id'] for c in categories], default=0) + 1
                
                # Create a temporary category for editing
                temp_category = {
                    'id': new_cat_id, 
                    'name': '',
                    'color': 'blue',
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                for i in range(0, max_capacity + 1):
                    # Clear only the sidebar portion of each line (not the entire line)
                    for j in range(15):  # Clear only columns 0-14
                        stdscr.addch(i, j, ' ')
                    
                    # Restore the separator line
                    stdscr.addch(i, 15, '│')
                
                # Redraw all categories in the sidebar with updated start_index
                pr.print_sidebar(
                    stdscr,
                    categories,
                    current_category_id,
                    sidebar_scroller.start_index,
                    max_capacity,
                    has_focus=True
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
                new_cat_name = ed.edit(stdscr, temp_category, pr.add_mode, 0, 0, is_sidebar=True)
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
                    
                    stdscr.attron(curses.color_pair(1))
                    stdscr.move(row, 0)
                    
                    # Append spaces
                    for j in range(15): 
                        stdscr.addch(row, j, ' ')
                        
                    # Redraw the separator
                    stdscr.attroff(curses.color_pair(1))
                    stdscr.addstr(row, 15, '│')
                    
                    # Position cursor at start of category name (1 char indent)
                    stdscr.move(row, 1)
                    stdscr.refresh()
                    
                    # Create a temporary copy for editing using the same mechanism as tasks
                    edit_cat = current_cat.copy()
                    edit_cat['description'] = current_cat['name']  # Map name to description for edit function
                    
                    new_name = ed.edit(stdscr, edit_cat, pr.edit_mode, 0, len(current_cat['name']), is_sidebar=True)
                    
                    if new_name:
                        # Enforce maximum length for category name
                        if len(new_name) > cat.MAX_CATEGORY_NAME_LENGTH:
                            new_name = new_name[:cat.MAX_CATEGORY_NAME_LENGTH]
                        cat.update_category_name(current_category_id, new_name)
                        categories = cat.load_categories()
                    pr.print_tasks_with_offset(stdscr, filtered_tasks, current_id, start, end, sidebar_width)
                    
                    curses.curs_set(0)
                    curses.noecho()
                    should_repaint = True
            
            elif key == curses.KEY_BACKSPACE or key == 127:
                # Delete selected category (with double backspace confirmation)
                if len(categories) > 0 and current_category_id != 0:
                    # Wait for second backspace
                    stdscr.addstr(max_capacity, sidebar_width, "Press backspace again to delete")
                    stdscr.refresh()
                    
                    # Wait for confirmation
                    k = stdscr.getch()
                    if k == curses.KEY_BACKSPACE or k == 127:
                        
                        # Handle tasks in this category
                        task_list = [task for task in task_list if task.get('category_id', 0) != current_category_id]
                        tsk.reassign_task_ids(task_list)
                        tsk.save_tasks(task_list, tsk.tasks_file_path)
                        cat.delete_category(current_category_id)
                        categories = cat.reassign_category_ids()
                        
                        # Update task category references to match new category IDs
                        # This is only necessary if we're renumbering categories
                        if len(categories) > 1:
                            # We need to reload tasks after renumbering to ensure proper associations
                            task_list = tsk.load_tasks()
                        
                        # Update sidebar scroller with new category count
                        sidebar_scroller.update_total(len(categories))
                        
                        # Select appropriate category after deletion
                        if len(categories) > 1:
                            new_index = len(categories) - 1
                            sidebar_scroller.current_index = new_index
                            current_category_id = categories[new_index]['id']
                        else:
                            sidebar_scroller.current_index = 0
                            current_category_id = 0

                        filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                        task_cnt = len(filtered_tasks)
                        
                        current_id = 1 if task_cnt > 0 else 0
                        current_row = 1 if task_cnt > 0 else 0
                        start = 1 if task_cnt > 0 else 0
                        end = task_cnt if task_cnt < max_capacity else max_capacity
                    
                    # Clear the status line
                    stdscr.move(max_capacity, 0)
                    stdscr.clrtoeol()
                    should_repaint = True
                
            elif key == ord(':'):
                curses.echo()
                curses.curs_set(1)
                
                # Disable timeout temporarily
                stdscr.timeout(-1)
                
                # Clear the bottom line before showing command prompt
                stdscr.move(max_capacity, 0)
                stdscr.clrtoeol()
                # Keep frames visible
                stdscr.addstr(max_y - 2, 0, "│")
                stdscr.addstr(max_y - 2, 15, "│")
                stdscr.addstr(max_y - 2, max_x - 1, "│")
                
                # Place the command input at the bottom of the screen, after the sidebar
                stdscr.addstr(max_capacity, sidebar_width, ":")
                stdscr.refresh()

                command_line = stdscr.getstr().decode('utf-8')
                stdscr.timeout(500)
                
                curses.curs_set(0)
                curses.noecho()
                
                command_result = cmd.execute_command(
                    stdscr,
                    command_line,
                    task_list,
                    filtered_tasks,
                    done_list,
                    purged_list,
                    current_id,
                    start,
                    end,
                    current_row,
                    max_capacity
                )

                # Check if we have categories in the result (special case for test/restore)
                if len(command_result) > 6:
                    task_list, done_list, current_id, current_row, start, end, categories, current_category_id = command_result
                    sidebar_scroller.update_total(len(categories))
                    
                    # Find the new category index
                    for i, c in enumerate(categories):
                        if c['id'] == current_category_id:
                            sidebar_scroller.current_index = i
                            break
                            
                    # Update filtered tasks for the new category
                    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                    task_cnt = len(filtered_tasks)
                else:
                    task_list, done_list, current_id, current_row, start, end = command_result
                
                should_repaint = True
                command_line = ""
                
        # Handle task navigation and actions when task area is focused
        elif focus_manager.is_tasks_focused():
            # Handle user input for tasks
            if key == ord('a'):
                if task_cnt == ed.max_task_count:
                    pr.print_msg(stdscr, pr.limit_msg)
                    stdscr.refresh()
                    time.sleep(1.2)
                    continue
                
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
                stdscr.move(y_pos, sidebar_width + ed.indent)
                stdscr.refresh()

                new_task = tsk.create_new_task(task_cnt + 1)
                new_task['category_id'] = 0 if current_category_id == 0 else current_category_id
                
                new_task_description = ed.edit(stdscr, new_task, pr.add_mode)
                
                if new_task_description != "":
                    new_id = task_cnt + 1
                    task_list = tsk.add_new_task(
                        task_list, new_id, new_task_description, False, new_task['category_id'])
                    task_cnt = task_cnt + 1
                    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                    
                    if task_cnt == 1:
                        start = 1
                    if task_cnt - 1 <= max_capacity:
                        current_row = task_cnt
                    else:
                        current_row = max_capacity
                    current_id = new_id
                    end = end + 1
                else:
                    start = old_start
                    end = old_end
                    should_repaint = True
                    curses.curs_set(0)
                    curses.noecho()
                    continue
                    
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
                if len(filtered_tasks) > 0 and current_id > 0:
                    task_idx = current_id - 1
                    
                    # Override the current task row y-position to account for sidebar
                    edit_row = current_row  # Row is correct, it's relative to visible area
                    
                    # Call edit_and_save with adjusted parameters for sidebar offset
                    stdscr.erase()
                    pr.print_status_bar(stdscr, done_cnt, len(filtered_tasks))
                    
                    # Display sidebar
                    pr.print_sidebar(
                        stdscr,
                        categories,
                        current_category_id,
                        sidebar_scroller.start_index,
                        max_capacity,
                        False
                    )
                    
                    pr.print_tasks_with_offset(stdscr, filtered_tasks, current_id, start, end, sidebar_width)
                    
                    # Move cursor to edit position
                    stdscr.move(edit_row, sidebar_width + ed.indent)
                    stdscr.refresh()
                    
                    # Use regular edit, but with the task offset in the interface
                    filtered_tasks[task_idx]['description'] = ed.edit(
                        stdscr, 
                        filtered_tasks[task_idx], 
                        pr.edit_mode
                    )
                    
                    # Handle task deletion if description is empty
                    if filtered_tasks[task_idx]['description'] == "":
                        task_uuid = filtered_tasks[task_idx]['uuid']
                        task_list = tsk.delete_task_by_uuid(task_list, task_uuid)
                        filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                        task_cnt = len(filtered_tasks)
                        
                        tsk.reassign_task_ids(task_list)
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
                        
                        pr.print_status_bar(stdscr, done_cnt, task_cnt)
                        stdscr.refresh()
                    
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
                # Try to restore data if in test mode, but don't fail if test module isn't available
                try:
                    import test.test as test_module
                    if test_module.is_test_mode_active():
                        test_module.restore_data()
                except ImportError:
                    # No test module found (PyPI installation), continue with normal exit
                    pass
                break
                
            elif key == ord(':'):
                curses.echo()
                curses.curs_set(1)
                
                # Disable timeout temporarily
                stdscr.timeout(-1)
                
                # Clear the bottom line
                stdscr.move(max_capacity, 0)
                stdscr.clrtoeol()
                # Keep frames visible
                stdscr.addstr(max_y - 2, 0, "│")
                stdscr.addstr(max_y - 2, 15, "│")
                stdscr.addstr(max_y - 2, max_x - 1, "│")
                
                stdscr.addstr(max_capacity, sidebar_width, ":")
                stdscr.refresh()
                command_line = stdscr.getstr().decode('utf-8')
                stdscr.timeout(500)
                
                curses.curs_set(0)
                curses.noecho()
                
                command_result = cmd.execute_command(
                    stdscr,
                    command_line,
                    task_list,
                    filtered_tasks,
                    done_list,
                    purged_list,
                    current_id,
                    start,
                    end,
                    current_row,
                    max_capacity
                )

                # Check if we have categories in the result (special case for test/restore)
                if len(command_result) > 6:
                    task_list, done_list, current_id, current_row, start, end, categories, current_category_id = command_result
                    sidebar_scroller.update_total(len(categories))
                    
                    # Find the new category index
                    for i, c in enumerate(categories):
                        if c['id'] == current_category_id:
                            sidebar_scroller.current_index = i
                            break  
                    # Update filtered tasks for the new category
                    filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                    task_cnt = len(filtered_tasks)
                else:
                    task_list, done_list, current_id, current_row, start, end = command_result
                
                should_repaint = True
                command_line = ""
                
            elif key == curses.KEY_UP:
                if task_cnt > 0:
                    start, end, current_id, current_row, should_repaint = nv.keyup_update(
                        start, end, current_id, current_row, task_cnt, max_capacity, True
                    )
                
            elif key == curses.KEY_DOWN:
                if task_cnt > 0:
                    start, end, current_id, current_row, should_repaint = nv.keydown_update(
                        start, end, current_id, current_row, task_cnt, max_capacity, True
                    )
                
            elif key == curses.KEY_BACKSPACE or key == 127:
                # Double backspace to delete a task
                k = stdscr.getch()
                if k == curses.KEY_BACKSPACE or k == 127:
                    if len(filtered_tasks) > 0:
                        if filtered_tasks[current_id - 1]['status'] is True:
                            done_cnt = done_cnt - 1
                        task_uuid = filtered_tasks[current_id - 1]['uuid']
                        task_list = tsk.delete_task_by_uuid(task_list, task_uuid)
                        filtered_tasks = tsk.get_tasks_by_category(task_list, current_category_id)
                        task_cnt = len(filtered_tasks)
                        current_id, current_row, start, end = nv.post_deletion_update(
                            current_id,
                            current_row,
                            start,
                            end,
                            task_cnt + 1,
                            max_capacity
                        )
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
