import time
import curses
import todoism.edit as ed
import todoism.task as tsk
import todoism.print as pr
import todoism.preference as pref
import todoism.command as cmd
import todoism.cli as cli
import todoism.category as cat
import todoism.navigate as nv
import todoism.message as msg
import todoism.keycode as kc
import todoism.color as clr
import todoism.state as st

def _sort_by_tag(categories):
    marked = []
    for i, task in enumerate(st.filtered_tasks):
        if _not_marked(task):
            marked = st.filtered_tasks[:i]
            break
    if len(st.filtered_tasks) > 0 and not _not_marked(st.filtered_tasks[len(st.filtered_tasks) - 1]):
            marked = st.filtered_tasks
    tsk.reassign_task_ids(marked)
    not_marked = []
    for c in categories:
        for task in st.filtered_tasks: 
            if _not_marked(task):
                if c['id'] == task['category_id']:
                    not_marked.append(task)
    tsk.reassign_task_ids(not_marked)
    for task in not_marked:
        task['id'] += len(marked)
    st.filtered_tasks = marked + not_marked

def _not_marked(task):
    if pref.get_sort_done() and pref.get_sort_flagged():
        return not task['status'] and not task['flagged']
    elif pref.get_sort_done():
        return not task['status']
    elif pref.get_sort_flagged():
        return not task['flagged']
    else:
        return False
        
def main(stdscr):
    stdscr.keypad(True)  # enable e.g arrow keys
    stdscr.scrollok(True)
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()
    
    curses.start_color()
    clr.setup_color_pairs()
    
    if kc.need_key_recording():
        if not kc.record_key_codes(stdscr):
            return
    
    keycodes = kc.get_key_codes()
    kc.CTRL_LEFT = keycodes['ctrl+left']
    kc.CTRL_RIGHT = keycodes['ctrl+right']
    kc.CTRL_SHIFT_LEFT = keycodes['ctrl+shift+left']
    kc.CTRL_SHIFT_RIGHT = keycodes['ctrl+shift+right']
    kc.ALT_LEFT = keycodes['alt+left']
    kc.ALT_RIGHT = keycodes['alt+right']
    
    pref.update_preferences()
    
    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

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
    st.focus_manager = nv.FocusManager()
    
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
    current_task_id = 1 if task_cnt > 0 else 0  # id of task selected
    current_task_row = 1 if task_cnt > 0 else 0  # range: [0, height-1]
    
    # Initialize task scrolling (using the original logic)
    start = 1 if task_cnt > 0 else 0
    end = task_cnt if task_cnt < max_capacity else max_capacity
    
    should_repaint = True
    
    # Set a timeout for getch() to make it non-blocking (500ms)
    stdscr.timeout(500)
    # Track when we last updated the time
    last_time_update = time.time()
    
    key = 0
    
    # Sidebar width
    sidebar_width = 16  # 15 for sidebar + 1 for separator
    task_scroll_offset = 0
    
    # setup state
    st.latest_max_x = max_x
    st.latest_max_y = max_y
    st.old_max_x = max_x
    st.old_max_y = max_y
    st.old_max_capacity = max_capacity
    st.latest_max_capacity = max_capacity
    st.current_task_id = current_task_id
    st.current_category_id = current_category_id
    st.start_task_id = start
    st.end_task_id = end
    st.current_task_row = current_task_row
    st.task_cnt = task_cnt 
    st.cat_cnt = len(categories)
    st.filtered_tasks = filtered_tasks
    
    while True:
        # Get filtered tasks for current category
        st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
        tsk.reassign_task_ids(st.filtered_tasks)
        
        if pref.get_sort_done():
            st.filtered_tasks = cmd.sort(st.filtered_tasks, 'status')
            tsk.reassign_task_ids(st.filtered_tasks)
        if pref.get_sort_flagged():
            st.filtered_tasks = cmd.sort(st.filtered_tasks, 'flagged')
            tsk.reassign_task_ids(st.filtered_tasks)
        
        _sort_by_tag(categories)
        
        st.task_cnt = len(st.filtered_tasks)
        st.done_cnt = tsk.done_count(st.filtered_tasks)
        st.cat_cnt = len(categories)

        st.old_max_x = st.latest_max_x
        # Handling window resizing
        st.latest_max_y, st.latest_max_x = stdscr.getmaxyx()
        st.latest_max_capacity = st.latest_max_y - 2
        
        # Prevent error when window is vertically too small
        if st.latest_max_capacity < 0:
            st.latest_max_capacity = 0
        
        # In case of window height change
        if st.latest_max_capacity != st.old_max_capacity:
            # Store if we're getting more or less space
            is_growing = st.latest_max_capacity > st.old_max_capacity
            
            # Update sidebar view
            sidebar_scroller.update_visible_height(st.latest_max_capacity)
            
            # Update task view
            if st.task_cnt > 0:
                if is_growing:
                    # WINDOW GROWING: Show maximum possible tasks while keeping current selection visible
                    # Calculate how much more space we have
                    
                    # Step 1: First attempt to fill from bottom
                    # Calculate how many more tasks we could show with new size
                    potential_end = min(st.task_cnt, st.start_task_id + st.latest_max_capacity - 1)

                    # Step 2: If we still have space after showing more at bottom, 
                    # show more at top too (if possible)
                    if potential_end - st.start_task_id + 1 < st.latest_max_capacity and st.start_task_id > 1:
                        # Calculate how much space is still available after filling bottom
                        remaining_space = st.latest_max_capacity - (potential_end - st.start_task_id + 1)

                        # Fill from top with remaining space
                        new_start = max(1, st.start_task_id - remaining_space)

                        # Update start and end
                        st.start_task_id = new_start
                        st.end_task_id = min(st.task_cnt, st.start_task_id + st.latest_max_capacity - 1)
                    else:
                        # Just extend end as much as possible
                        st.end_task_id = potential_end

                    # Step 3: Special case for when we're near the end of the list
                    # If we're not showing the maximum possible tasks, pull the window up
                    visible_count = st.end_task_id - st.start_task_id + 1
                    if visible_count < st.latest_max_capacity and st.end_task_id < st.task_cnt:
                        # We have empty space but more tasks below - adjust both ends
                        st.end_task_id = min(st.task_cnt, st.end_task_id + (st.latest_max_capacity - visible_count))
                        visible_count = st.end_task_id - st.start_task_id + 1

                        if visible_count < st.latest_max_capacity and st.start_task_id > 1:
                            # Still have space? Pull up from top too
                            spaces_to_fill = st.latest_max_capacity - visible_count
                            st.start_task_id = max(1, st.start_task_id - spaces_to_fill)
                            st.end_task_id = min(st.task_cnt, st.start_task_id + st.latest_max_capacity - 1)

                    # Step 4: Special case when we're at the end of the list
                    # If end is at max and we have space, pull window up
                    if st.end_task_id == st.task_cnt and st.end_task_id - st.start_task_id + 1 < st.latest_max_capacity and st.start_task_id > 1:
                        # Calculate how many more items we could show at top
                        available_slots = st.latest_max_capacity - (st.end_task_id - st.start_task_id + 1)
                        new_start = max(1, st.start_task_id - available_slots)
                        st.start_task_id = new_start

                    # Make sure current task stays visible by adjusting view if needed
                    if st.current_task_id < st.start_task_id:
                        # If current task would be above visible area, adjust view
                        st.start_task_id = st.current_task_id
                        st.end_task_id = min(st.task_cnt, st.start_task_id + st.latest_max_capacity - 1)
                    elif st.current_task_id > st.end_task_id:
                        # If current task would be below visible area, adjust view
                        st.end_task_id = st.current_task_id
                        st.start_task_id = max(1, st.end_task_id - st.latest_max_capacity + 1)

                    # Update current_task_row based on adjusted start/end
                    st.current_task_row = st.current_task_id - st.start_task_id + 1
                else:
                    # WINDOW SHRINKING: Keep current task visible but reduce what's shown
                    # Make sure end doesn't exceed capacity from start
                    if st.end_task_id > st.start_task_id + st.latest_max_capacity - 1:
                        st.end_task_id = st.start_task_id + st.latest_max_capacity - 1
                        
                    # If end exceeds task count, adjust both end and start
                    if st.end_task_id > st.task_cnt:
                        st.end_task_id = st.task_cnt
                        st.start_task_id = max(1, st.end_task_id - st.latest_max_capacity + 1)
                        
                    # Make sure current task is still visible by adjusting start if needed
                    if st.current_task_id < st.start_task_id:
                        st.start_task_id = st.current_task_id
                        st.end_task_id = min(st.start_task_id + st.latest_max_capacity - 1, st.task_cnt)
                    elif st.current_task_id > st.end_task_id:
                        st.end_task_id = st.current_task_id
                        st.start_task_id = max(1, st.end_task_id - st.latest_max_capacity + 1)
        
        # Window was resized
        if st.old_max_x != st.latest_max_x or st.latest_max_capacity != st.old_max_capacity:
            st.old_max_capacity = st.latest_max_capacity
            should_repaint = True
            continue
        
        # Check if we need to update the time (every second)
        current_time = time.time()
        if current_time - last_time_update >= 2.0:  # Increased to 2 seconds to reduce lag
            pr.print_status_bar(stdscr)
            stdscr.refresh()
            last_time_update = current_time
            
        if should_repaint:
            tsk.reassign_task_ids(st.filtered_tasks)
            if st.focus_manager.is_tasks_focused():
                if st.task_cnt > 0:
                    if st.current_task_id > st.task_cnt:
                        st.current_task_id = st.task_cnt
                        st.current_task_row = min(st.current_task_row, st.latest_max_capacity)
                    
                    # Render the main view with sidebar
                    pr.print_whole_view(
                        stdscr,
                        categories,
                        sidebar_scroller.start_index,
                    )
                else:
                    # No tasks in current category
                    pr.print_category_entries(
                        stdscr,
                        categories,
                        sidebar_scroller.start_index,
                    )
                    pr.print_frame_all(stdscr)
                    pr.print_msg_in_task_panel(stdscr, msg.empty_msg, 16, highlight=True)
                    pr.print_status_bar(stdscr)

            else:
                pr.print_whole_view(
                    stdscr,
                    categories,
                    sidebar_scroller.start_index,
                )

            should_repaint = False
            
        # Wait for user input
        key = stdscr.getch()
                
        if key == -1:
            continue
            
        if key == 9:  # Tab key for switching focus
            st.focus_manager.toggle_focus()
            should_repaint = True
            continue
            
        if key == curses.KEY_MOUSE:
            try:
                mouse_id, mouse_x, mouse_y, mouse_z, button_state = curses.getmouse()
                
                if mouse_x < sidebar_width:
                    if not st.focus_manager.is_sidebar_focused():
                        st.focus_manager.toggle_focus()
                        should_repaint = True
                    
                    # Only handle category selection if clicked on a valid category
                    if 1 <= mouse_y <= min(len(categories), st.latest_max_capacity):
                        clicked_cat_index = sidebar_scroller.start_index + mouse_y - 1
                        
                        if 0 <= clicked_cat_index < len(categories):
                            old_category_id = st.current_category_id
                            sidebar_scroller.current_index = clicked_cat_index
                            st.current_category_id = categories[clicked_cat_index]['id']
                            
                            if old_category_id != st.current_category_id:
                                st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                                st.task_cnt = len(st.filtered_tasks)
                                st.current_task_id = 1 if st.task_cnt > 0 else 0
                                st.current_task_row = 1 if st.task_cnt > 0 else 0
                                st.start_task_id = 1 if st.task_cnt > 0 else 0
                                st.end_task_id = st.task_cnt if st.task_cnt < st.latest_max_capacity else st.latest_max_capacity
                                should_repaint = True
                    continue
                
                # Handle clicks in task area (including blank areas)
                if mouse_x >= sidebar_width:
                    if not st.focus_manager.is_tasks_focused():
                        st.focus_manager.toggle_focus()
                        should_repaint = True
                    
                    # Only handle task selection if clicked on a valid task row
                    if 1 <= mouse_y <= min(st.task_cnt, st.latest_max_capacity):
                        clicked_task_id = st.start_task_id + mouse_y - 1
                        clicked_task_row = mouse_y  # Row on screen
                        
                        if st.start_task_id <= clicked_task_id <= st.end_task_id:
                            task_index = clicked_task_id - 1
                            
                            flag_x_start = sidebar_width + 3
                            flag_x_end = flag_x_start + 1 
                            
                            status_x_start = sidebar_width + 5
                            status_x_end = status_x_start + 1

                            if flag_x_start <= mouse_x <= flag_x_end:
                                if st.filtered_tasks:
                                    st.filtered_tasks[task_index]['flagged'] = not st.filtered_tasks[task_index]['flagged']
                                    tsk.save_tasks(task_list)
                            elif status_x_start <= mouse_x <= status_x_end:
                                if st.filtered_tasks:
                                    done_list.append(st.filtered_tasks[task_index])
                                    st.filtered_tasks[task_index]['status'] = not st.filtered_tasks[task_index]['status']
                                    tsk.save_tasks(task_list)
                            else:
                                st.current_task_id = clicked_task_id
                                st.current_task_row = clicked_task_row
                            should_repaint = True
            except curses.error:
                # getmouse() can raise an exception if the terminal doesn't support mouse
                pass
            continue
        
        if st.focus_manager.is_sidebar_focused():
            if key == curses.KEY_UP:
                task_scroll_offset = 0
                sidebar_scroller.scroll_up()
                if len(categories) > 0:
                    st.current_category_id = categories[sidebar_scroller.current_index]['id']
                    
                    # Reset task selection for the new category
                    st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                    st.task_cnt = len(st.filtered_tasks)
                    st.current_task_id = 1 if st.task_cnt > 0 else 0
                    st.current_task_row = 1 if st.task_cnt > 0 else 0
                    st.start_task_id = 1 if st.task_cnt > 0 else 0
                    st.end_task_id = st.task_cnt if st.task_cnt < st.latest_max_capacity else st.latest_max_capacity

                should_repaint = True
                
            elif key == curses.KEY_DOWN:
                task_scroll_offset = 0
                sidebar_scroller.scroll_down()
                if len(categories) > 0:
                    st.current_category_id = categories[sidebar_scroller.current_index]['id']
                    
                    # Reset task selection for the new category
                    st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                    st.task_cnt = len(st.filtered_tasks)
                    st.current_task_id = 1 if st.task_cnt > 0 else 0
                    st.current_task_row = 1 if st.task_cnt > 0 else 0
                    st.start_task_id = 1 if st.task_cnt > 0 else 0
                    st.end_task_id = st.task_cnt if st.task_cnt < st.latest_max_capacity else st.latest_max_capacity
                    
                should_repaint = True
            
            elif key == ord('q'):
                # Always backup normal data on exit
                import todoism.backup as backup
                backup.backup_normal_data()
                
                try:
                    import test.test as test_module
                    if test_module.is_dev_mode_active():
                        test_module.exit_dev_mode()
                except ImportError:
                    # No test module found (PyPI installation), continue with normal exit
                    pass
                break
                
            elif key == ord('a'):
                curses.echo()
                curses.curs_set(1)
                
                # Calculate the position where new category would appear
                cat_count = len(categories)
                visible_count = min(cat_count, st.latest_max_capacity)
                is_sidebar_full = visible_count >= st.latest_max_capacity
                if is_sidebar_full:
                    # scroll up
                    sidebar_scroller.start_index += 1
                    new_cat_row = st.latest_max_capacity
                else:
                    new_cat_row = visible_count + 1
                    
                new_cat_id = max([c['id'] for c in categories], default=0) + 1
                
                # Create a temporary category for editing
                temp_category = {
                    'id': new_cat_id, 
                    'name': ''
                }
                
                for i in range(0, st.latest_max_capacity + 1):
                    # Clear only the sidebar portion of each line (not the entire line)
                    for j in range(15):  # Clear only columns 0-14
                        stdscr.addch(i, j, ' ')
                    
                    # Restore the separator line
                    stdscr.addch(i, 15, '│')
                
                # Redraw all categories in the sidebar with updated start_index
                pr.print_category_entries(
                    stdscr,
                    categories,
                    sidebar_scroller.start_index,
                )
                
                pr.print_left_frame(stdscr, st.latest_max_y)
                pr.print_sidebar_task_panel_separator(stdscr, st.latest_max_y)
                pr.print_right_frame(stdscr, st.latest_max_y, st.latest_max_x)
                if st.task_cnt > 0:
                    pr.print_task_entries(stdscr, 16)
                else: 
                    pr.print_msg_in_task_panel(stdscr, msg.empty_msg, 16, highlight=False)
                pr.print_status_bar(stdscr)
                
                stdscr.refresh()

                # Print new category placeholder
                stdscr.addstr(new_cat_row, 0, f"{new_cat_id:2d} ")
                
                # Move cursor to the consistent 1-space indent position
                stdscr.move(new_cat_row, 1)  # 1-space indent, matching print_category()
                stdscr.refresh()
                
                # Use the same edit function as for tasks, but adapt for sidebar position
                temp_category['description'] = ''  # Add this field for edit function compatibility
                new_cat_name = ed.edit(stdscr, temp_category, pr.add_mode, 0, 0)
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
                                st.current_category_id = new_cat['id']
                                break
                                
                        # Update filtered tasks for the new category
                        st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                        st.task_cnt = len(st.filtered_tasks)
                        st.current_task_id = 1 if st.task_cnt > 0 else 0
                        st.current_task_row = 1 if st.task_cnt > 0 else 0
                        st.start_task_id = 1 if st.task_cnt > 0 else 0
                        st.end_task_id = st.task_cnt if st.task_cnt < st.latest_max_capacity else st.latest_max_capacity
                        st.cat_cnt = len(categories)
                
                curses.curs_set(0)
                curses.noecho()
                should_repaint = True
                
            elif key == ord('e'):
                # Edit category name with scrolling (skip for "All" category)
                if len(categories) > 0 and st.current_category_id != 0:
                    curses.echo()
                    curses.curs_set(1)
                    
                    # Get current category to edit
                    current_cat = categories[sidebar_scroller.current_index]
                    row = sidebar_scroller.current_index - sidebar_scroller.start_index + 1
                    
                    pr.print_status_bar(stdscr)
                    
                    # Draw all categories
                    pr.print_category_entries(
                        stdscr,
                        categories,
                        sidebar_scroller.start_index,
                    )
                    
                    pr.print_left_frame(stdscr, st.latest_max_y)
                    pr.print_sidebar_task_panel_separator(stdscr, st.latest_max_y)
                    pr.print_task_entries(stdscr, sidebar_width)
                    
                    stdscr.attron(curses.color_pair(clr.get_theme_color_pair_num_text()))
                    stdscr.move(row, 0)
                    
                    # Append spaces
                    for j in range(15): 
                        stdscr.addch(row, j, ' ')
                        
                    # Redraw the separator
                    stdscr.attroff(curses.color_pair(clr.get_theme_color_pair_num_text()))
                    stdscr.addstr(row, 15, '│')
                    
                    # Position cursor at start of category name (1 char indent)
                    stdscr.move(row, 1)
                    stdscr.refresh()
                    
                    # Create a temporary copy for editing using the same mechanism as tasks
                    edit_cat = current_cat.copy()
                    edit_cat['description'] = current_cat['name']  # Map name to description for edit function
                    
                    new_name = ed.edit(stdscr, edit_cat, pr.edit_mode, 0, len(current_cat['name']))
                    
                    if new_name:
                        # Enforce maximum length for category name
                        if len(new_name) > cat.MAX_CATEGORY_NAME_LENGTH:
                            new_name = new_name[:cat.MAX_CATEGORY_NAME_LENGTH]
                        cat.update_category_name(st.current_category_id, new_name)
                        categories = cat.load_categories()
                    pr.print_task_entries(stdscr, sidebar_width)
                    
                    curses.curs_set(0)
                    curses.noecho()
                    should_repaint = True
            
            elif key == curses.KEY_BACKSPACE or key == kc.BACKSPACE:
                # Delete selected category (with double backspace confirmation)
                if len(categories) > 0 and st.current_category_id != 0:
                    # Wait for second backspace
                    stdscr.addstr(st.latest_max_capacity, sidebar_width, "Press backspace again to delete")
                    stdscr.refresh()
                    
                    # Wait for confirmation
                    k = stdscr.getch()
                    if k == curses.KEY_BACKSPACE or k == kc.BACKSPACE:
                        
                        # Handle tasks in this category
                        task_list = [task for task in task_list if task.get('category_id', 0) != st.current_category_id]
                        tsk.reassign_task_ids(task_list)
                        tsk.save_tasks(task_list)
                        cat.delete_category(st.current_category_id)
                        categories = cat.reassign_category_ids()
                        
                        for task in task_list:
                            if task['category_id'] > st.current_category_id:
                                task['category_id'] -= 1
                        tsk.save_tasks(task_list)
                        
                        # Update task category references to match new category IDs
                        # This is only necessary if we're renumbering categories
                        if len(categories) > 1:
                            # We need to reload tasks after renumbering to ensure proper associations
                            task_list = tsk.load_tasks()
                        
                        # Update sidebar scroller with new category count
                        sidebar_scroller.update_total(len(categories))
                        
                        # Only category id if the last category was deleted
                        if len(categories) == st.current_category_id:
                            new_index = st.current_category_id - 1
                            sidebar_scroller.current_index = new_index
                            st.current_category_id = categories[new_index]['id']

                        st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                        st.task_cnt = len(st.filtered_tasks)
                        
                        st.current_task_id = 1 if st.task_cnt > 0 else 0
                        st.current_task_row = 1 if st.task_cnt > 0 else 0
                        st.start_task_id = 1 if st.task_cnt > 0 else 0
                        st.end_task_id = st.task_cnt if st.task_cnt < st.latest_max_capacity else st.latest_max_capacity
                    
                    # Clear the status line
                    stdscr.move(st.latest_max_capacity, 0)
                    stdscr.clrtoeol()
                    should_repaint = True
                
            elif key == ord(':'):
                curses.echo()
                curses.curs_set(1)
                
                # Disable timeout temporarily
                stdscr.timeout(-1)
                
                # Clear the bottom line before showing command prompt
                stdscr.move(st.latest_max_capacity, 0)
                stdscr.clrtoeol()
                # Keep frames visible
                stdscr.addstr(st.latest_max_y - 2, 0, "│")
                stdscr.addstr(st.latest_max_y - 2, 15, "│")
                stdscr.addstr(st.latest_max_y - 2, st.latest_max_x - 1, "│")
                
                # Place the command input at the bottom of the screen, after the sidebar
                stdscr.addstr(st.latest_max_capacity, sidebar_width, ":")
                stdscr.refresh()

                command_line = stdscr.getstr().decode('utf-8')
                stdscr.timeout(500)
                
                curses.curs_set(0)
                curses.noecho()
                
                command_result = cmd.execute_command(
                    stdscr,
                    command_line,
                    task_list,
                    done_list,
                    purged_list,
                )

                # Check if we have categories in the result (special case for test/restore)
                if len(command_result) > 2:
                    task_list, done_list, categories = command_result
                    sidebar_scroller.update_total(len(categories))
                    
                    # Find the new category index
                    for i, c in enumerate(categories):
                        if c['id'] == st.current_category_id:
                            sidebar_scroller.current_index = i
                            break
                            
                    # Update filtered tasks for the new category
                    st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                    st.task_cnt = len(st.filtered_tasks)
                else:
                    task_list, done_list = command_result
                
                should_repaint = True
                command_line = ""
                
        # Handle task navigation and actions when task area is focused
        elif st.focus_manager.is_tasks_focused():
            # Handle user input for tasks
            if key == ord('a'):
                if st.task_cnt == tsk.MAX_TASK_COUNT:
                    pr.print_msg(stdscr, msg.limit_msg)
                    stdscr.refresh()
                    time.sleep(1.2)
                    continue
                
                curses.echo()
                curses.curs_set(1)
                
                # Store old values for potential rollback
                old_start = st.start_task_id
                old_end = st.end_task_id
                
                # adjust start end for pre-print
                # taskoverflow if a new one is added:
                if st.task_cnt >= st.latest_max_capacity:
                    if st.end_task_id <= st.task_cnt:
                        st.start_task_id = st.task_cnt - (st.end_task_id - st.start_task_id - 1)
                        st.end_task_id = st.task_cnt

                pr.print_category_entries(
                    stdscr,
                    categories,
                    sidebar_scroller.start_index,
                )
                
                pr.print_left_frame(stdscr, st.latest_max_y)
                pr.print_sidebar_task_panel_separator(stdscr, st.latest_max_y)
                
                st.adding_task = True
                # Print existing tasks with offset (crucial: pass sidebar_width to offset tasks)
                pr.print_task_entries(stdscr, sidebar_width)

                # Add a new task with proper indentation
                new_task_num = f"{st.task_cnt + 1:2d}"
                y_pos = st.latest_max_capacity if st.task_cnt >= st.latest_max_capacity else st.task_cnt + 1
                stdscr.addstr(y_pos, sidebar_width, f"{new_task_num} ")

                # Move cursor to the correct position after task number
                stdscr.move(y_pos, sidebar_width + tsk.TASK_INDENT_IN_TASK_PANEL)
                stdscr.refresh()

                new_task = tsk.create_new_task(st.task_cnt + 1)
                new_task['category_id'] = 0 if st.current_category_id == 0 else st.current_category_id
                
                
                new_task_description = ed.edit(stdscr, new_task, pr.add_mode)
                st.adding_task = False
                
                if new_task_description != "":
                    new_id = st.task_cnt + 1
                    task_list = tsk.add_new_task(
                        task_list, new_id, new_task_description, False, new_task['category_id'])
                    st.task_cnt = st.task_cnt + 1
                    st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                    
                    if st.task_cnt == 1:
                        st.start_task_id = 1
                    if st.task_cnt - 1 <= st.latest_max_capacity:
                        st.current_task_row = st.task_cnt
                    else:
                        st.current_task_row = st.latest_max_capacity
                    st.current_task_id = new_id
                    st.end_task_id = st.end_task_id + 1
                else:
                    st.start_task_id = old_start
                    st.end_task_id = old_end
                    should_repaint = True
                    curses.curs_set(0)
                    curses.noecho()
                    continue
                    
                stdscr.refresh()
                curses.curs_set(0)
                curses.noecho()
                
            elif key == ord('d') or key == ord(' '):
                # mark the current task as 'done'
                if st.filtered_tasks and st.current_task_id > 0:
                    task_idx = st.current_task_id - 1
                    done_list.append(st.filtered_tasks[task_idx])
                    st.filtered_tasks[task_idx]['status'] = not st.filtered_tasks[task_idx]['status']
                    tsk.save_tasks(task_list)
                    should_repaint = True
                    
            elif key == ord('e'):
                curses.echo()
                curses.curs_set(1)
                if len(st.filtered_tasks) > 0 and st.current_task_id > 0:
                    task_idx = st.current_task_id - 1
                    
                    # Override the current task row y-position to account for sidebar
                    edit_row = st.current_task_row  # Row is correct, it's relative to visible area
                    st.task_cnt = len(st.filtered_tasks)
                    pr.print_status_bar(stdscr)
                    
                    pr.print_category_entries(
                        stdscr,
                        categories,
                        sidebar_scroller.start_index,
                    )
                    pr.print_left_frame(stdscr, st.latest_max_y)
                    pr.print_sidebar_task_panel_separator(stdscr, st.latest_max_y)
                    pr.print_task_entries(stdscr, sidebar_width)
                    
                    # Move cursor to edit position
                    stdscr.move(edit_row, sidebar_width + tsk.TASK_INDENT_IN_TASK_PANEL)
                    stdscr.refresh()
                    
                    st.filtered_tasks[task_idx]['description'] = ed.edit(
                        stdscr, 
                        st.filtered_tasks[task_idx], 
                        pr.edit_mode
                    )
                    
                    if st.filtered_tasks[task_idx]['description'] == "":
                        task_uuid = st.filtered_tasks[task_idx]['uuid']
                        task_list = tsk.delete_task_by_uuid(task_list, task_uuid)
                        st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                        st.task_cnt = len(st.filtered_tasks)
                        
                        # Adjust selection after deletion
                        if st.task_cnt == 0:
                            st.current_task_id = 0
                            st.current_task_row = 0
                            st.start_task_id = 0
                            st.end_task_id = 0
                            # Clear task area and show empty message
                            for i in range(1, st.latest_max_capacity + 1):
                                stdscr.move(i, sidebar_width)
                                stdscr.clrtoeol()
                        else:
                            # Keep the same visual position if possible
                            if st.current_task_id > st.task_cnt:
                                st.current_task_id = st.task_cnt
                            
                            # Adjust scroll range
                            if st.end_task_id > st.task_cnt:
                                st.end_task_id = st.task_cnt
                                st.start_task_id = max(1, st.end_task_id - st.latest_max_capacity + 1)
                            
                            # Update current row
                            st.current_task_row = st.current_task_id - st.start_task_id + 1
                            
                            # Start redraw from one row above the deleted position
                            start_redraw = max(1, st.current_task_row - 1)
                            
                            # Update tasks from one row above deletion
                            for i in range(start_redraw, min(st.task_cnt - st.start_task_id + 2, st.latest_max_capacity + 1)):
                                y = i
                                task_index = st.start_task_id + i - 1
                                
                                # Clear just this line
                                stdscr.move(y, sidebar_width)
                                stdscr.clrtoeol()
                                
                                # Render the task if it exists
                                if task_index < st.task_cnt:
                                    pr.render_task(
                                        stdscr,
                                        st.filtered_tasks[task_index],
                                        y,
                                        task_index + 1 == st.current_task_id,
                                        max_x=max_x
                                    )
                            
                            # Clear the last line if needed
                            if st.task_cnt - st.start_task_id + 1 < st.latest_max_capacity:
                                stdscr.move(st.task_cnt - st.start_task_id + 2, sidebar_width)
                                stdscr.clrtoeol()
                        
                        pr.print_status_bar(stdscr)
                        stdscr.refresh()
                    
                    tsk.save_tasks(task_list)
                    should_repaint = True
                    
                curses.curs_set(0)
                curses.noecho()
                
            elif key == ord('f'):
                if st.filtered_tasks and st.current_task_id > 0:
                    task_idx = st.current_task_id - 1
                    st.filtered_tasks[task_idx]['flagged'] = not st.filtered_tasks[task_idx]['flagged']
                    tsk.save_tasks(task_list)
                    should_repaint = True
            elif key == curses.KEY_RIGHT:
                task_scroll_offset += 1
                pr.render_task(stdscr, st.filtered_tasks[st.current_task_id - 1], st.current_task_row, True, task_scroll_offset) 
            elif key == curses.KEY_LEFT:
                task_scroll_offset = max(0, task_scroll_offset - 1)
                pr.render_task(stdscr, st.filtered_tasks[st.current_task_id - 1], st.current_task_row, True, task_scroll_offset)
            elif key == ord('q'):
                # Always backup normal data on exit
                import todoism.backup as backup
                backup.backup_normal_data()
                try:
                    import test.test as test_module
                    if test_module.is_dev_mode_active():
                        test_module.exit_dev_mode()
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
                stdscr.move(st.latest_max_capacity, 0)
                stdscr.clrtoeol()
                # Keep frames visible
                stdscr.addstr(st.latest_max_y - 2, 0, "│")
                stdscr.addstr(st.latest_max_y - 2, 15, "│")
                stdscr.addstr(st.latest_max_y - 2, st.latest_max_x - 1, "│")
                
                stdscr.addstr(st.latest_max_capacity, sidebar_width, ":")
                stdscr.refresh()
                command_line = stdscr.getstr().decode('utf-8')
                stdscr.timeout(500)
                
                curses.curs_set(0)
                curses.noecho()
                
                command_result = cmd.execute_command(
                    stdscr,
                    command_line,
                    task_list,
                    done_list,
                    purged_list,
                )

                # Check if we have categories in the result (special case for test/restore)
                if len(command_result) > 2:
                    task_list, done_list, categories = command_result
                    sidebar_scroller.update_total(len(categories))
                    
                    # Find the new category index
                    for i, c in enumerate(categories):
                        if c['id'] == st.current_category_id:
                            sidebar_scroller.current_index = i
                            break  
                    # Update filtered tasks for the new category
                    st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                    st.task_cnt = len(st.filtered_tasks)
                else:
                    task_list, done_list = command_result
                
                should_repaint = True
                command_line = ""
                
            elif key == curses.KEY_UP:
                task_scroll_offset = 0
                if st.task_cnt > 0:
                    should_repaint = nv.keyup_update(st.task_cnt, True)
            elif key == curses.KEY_DOWN:
                task_scroll_offset = 0
                if st.task_cnt > 0:
                    should_repaint = nv.keydown_update(st.task_cnt, True)
                
            elif key == curses.KEY_BACKSPACE or key == kc.BACKSPACE:
                # Double backspace to delete a task
                k = stdscr.getch()
                if k == curses.KEY_BACKSPACE or k == kc.BACKSPACE:
                    if len(st.filtered_tasks) > 0:
                        if st.filtered_tasks[st.current_task_id - 1]['status'] is True:
                            st.done_cnt = st.done_cnt - 1
                        task_uuid = st.filtered_tasks[st.current_task_id - 1]['uuid']
                        task_list = tsk.delete_task_by_uuid(task_list, task_uuid)
                        st.filtered_tasks = tsk.get_tasks_by_category(task_list, st.current_category_id)
                        st.task_cnt = len(st.filtered_tasks)
                        nv.post_deletion_update(st.task_cnt + 1)
                    tsk.save_tasks(task_list)
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
