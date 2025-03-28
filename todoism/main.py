import time
import curses

import todoism.edit as ed
import todoism.task as tsk
import todoism.print as pr
import todoism.preference as pref
import todoism.command as cmd
import todoism.category as cat
import todoism.navigate as nv
import todoism.message as msg
import todoism.keycode as kc
import todoism.color as clr
import todoism.state as st
import todoism.search as srch
import todoism.safe as sf
import todoism.due as due 
import todoism.update as up

def _quit_search(stdscr, task_list):
    st.searching = False
    pr.clear_bottom_bar_except_status(stdscr)
    _restore_state(task_list)

def _handle_command_input(stdscr):
    curses.echo()
    curses.curs_set(1)
    stdscr.timeout(-1)
    pr.clear_bottom_bar_except_status(stdscr)
    sf.safe_addstr(stdscr, st.latest_max_y - 2, 1, ":")
    stdscr.refresh()
    command = stdscr.getstr().decode("utf-8")
    stdscr.timeout(500)
    curses.curs_set(0)
    curses.noecho()
    return command

def _handle_dev_restore(categories, task_list, sidebar_scroller):
    sidebar_scroller.update_total(len(categories))
    for i, c in enumerate(categories):
        if c["id"] == st.current_category_id:
            sidebar_scroller.current_index = i
            break
        
    st.filtered_tasks = tsk.get_tasks_by_category_id(task_list, st.current_category_id)
    return categories  
    
def _restore_task_panel(task_list, categories):
    _restore_state(task_list)
    _sort_by_flagged_done_tag(categories)

def _restore_state(task_list):    
    st.filtered_tasks = tsk.get_tasks_by_category_id(task_list, st.current_category_id)
    st.task_cnt = len(st.filtered_tasks)
    st.current_task_id = 1 if st.task_cnt > 0 else 0
    st.current_task_row = 1 if st.task_cnt > 0 else 0
    st.start_task_id = 1 if st.task_cnt > 0 else 0
    st.end_task_id = min(st.latest_max_capacity, st.task_cnt)

def _window_resized():
    return st.old_max_x != st.latest_max_x or st.latest_max_y != st.old_max_y

def _sort_by_tag(categories):
    marked = []
    for i, task in enumerate(st.filtered_tasks):
        if _task_not_marked(task):
            marked = st.filtered_tasks[:i]
            break
    if len(st.filtered_tasks) > 0 and not _task_not_marked(st.filtered_tasks[len(st.filtered_tasks) - 1]):
            marked = st.filtered_tasks
    not_marked = []
    for c in categories:
        for task in st.filtered_tasks: 
            if _task_not_marked(task) and c["id"] == task["category_id"]:
                    not_marked.append(task)
    st.filtered_tasks = marked + not_marked
    tsk.reassign_task_ids(st.filtered_tasks)
    
def _sort_by_flagged_done_tag(categories):
    if pref.get_sort_by_done():
        st.filtered_tasks = tsk.sort(st.filtered_tasks, "status")
        tsk.reassign_task_ids(st.filtered_tasks)
    if pref.get_sort_by_flagged():
        st.filtered_tasks = tsk.sort(st.filtered_tasks, "flagged")
        tsk.reassign_task_ids(st.filtered_tasks)
    _sort_by_tag(categories)

def _task_not_marked(task):
    if pref.get_sort_by_done() and pref.get_sort_by_flagged():
        return not task["status"] and not task["flagged"]
    elif pref.get_sort_by_done():
        return not task["status"]
    elif pref.get_sort_by_flagged():
        return not task["flagged"]
    else:
        return False
    
def main(stdscr):
    stdscr.keypad(True)  # enable e.g arrow keys
    stdscr.scrollok(True)
    curses.curs_set(0)
    curses.set_escdelay(25) # faster escape key
    curses.mouseinterval(0) # faster mouse click
    stdscr.clear()
    stdscr.refresh()
    curses.start_color()
    clr.setup_color_pairs()
    stdscr.bkgd(' ', clr.get_bkg_color_pair())
    
    if kc.need_key_recording():
        if not kc.record_key_codes(stdscr):
            return
    kc.setup_keycodes()

    pref.update_preferences()    
    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    # Update existing tasks to include category_id if missing
    task_list = tsk.update_existing_tasks()
    due.add_due_key_if_missing(task_list)
    tsk.save_tasks(task_list)
    tsk.reassign_task_ids(task_list)
    categories = cat.load_categories()
        
    # Set a timeout for getch() to make it non-blocking (500ms)
    # 500ms makes sure double backspaces work
    stdscr.timeout(500)
    last_time_update = time.time()
    
    should_repaint = True
    task_scroll_offset = 0
    
    max_y, max_x = stdscr.getmaxyx()
    # setup state
    st.latest_max_x = max_x
    st.latest_max_y = max_y
    st.old_max_x = max_x
    st.old_max_y = max_y
    st.old_max_capacity = max_y - 2 - 2
    st.latest_max_capacity = max_y - 2 - 2
    st.current_category_id = 0
    st.cat_cnt = len(categories)
    st.filtered_tasks = tsk.get_tasks_by_category_id(task_list, st.current_category_id)
    st.task_cnt = len(st.filtered_tasks)
    st.current_task_row = 1 if st.task_cnt > 0 else 0
    st.current_task_id = 1 if st.task_cnt > 0 else 0
    st.start_task_id = 1 if st.task_cnt > 0 else 0
    st.end_task_id = st.task_cnt if st.task_cnt < st.latest_max_capacity else st.latest_max_capacity
    
    st.focus_manager = nv.FocusManager()
    sidebar_scroller = nv.SidebarScroller(len(categories), st.latest_max_capacity)
    
    update_available = up.check_for_updates()
    if update_available:
        pr.print_outer_frame(stdscr)
        pr.print_msg(stdscr, msg.NEW_VERSION_MSG)

        # Wait for user response
        while True:
            key = stdscr.getch()
            if key == kc.ENTER or curses.KEY_ENTER:
                break
            elif key == ord('u'):
                success = up.update_todoism()
                if success:
                    pr.clear_all_except_outer_frames(stdscr)
                    pr.print_msg(stdscr, msg.UPDATE_SUCCESS_MSG)
                    stdscr.refresh()
                    while True:
                        key = stdscr.getch()
                        if key == ord('q'):
                            return
                else:
                    pr.clear_all_except_outer_frames(stdscr)
                    pr.print_msg(stdscr, msg.UPDATE_FAILURE_MSG)
                    stdscr.refresh()
                    time.sleep(2)
                    break
    
    while True:
        if not st.searching:
            st.filtered_tasks = tsk.get_tasks_by_category_id(task_list, st.current_category_id)
        tsk.reassign_task_ids(st.filtered_tasks)
        
        _sort_by_flagged_done_tag(categories)
        
        st.task_cnt = len(st.filtered_tasks)
        st.cat_cnt = len(categories)

        # Update window dimension in every iteration
        st.old_max_y = st.latest_max_y        
        st.old_max_x = st.latest_max_x
        st.latest_max_y, st.latest_max_x = stdscr.getmaxyx()
        st.old_max_capacity = st.latest_max_capacity
        st.latest_max_capacity = st.latest_max_y - 2 - 2
        
        # Prevent error when window is vertically too small
        if st.latest_max_capacity < 0:
            st.latest_max_capacity = 0
        
        # In case of max_capacity change
        if st.latest_max_capacity != st.old_max_capacity:
            is_growing = st.latest_max_capacity > st.old_max_capacity
            
            # Update sidebar view
            sidebar_scroller.update_visible_height(st.latest_max_capacity)
            
            # Update task view
            if st.task_cnt > 0:
                if is_growing:
                    # WINDOW GROWING: Show maximum possible tasks while keeping current selection visible
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
                        
        if _window_resized():
            should_repaint = True
            stdscr.clear()
            continue
        
        # Check if we need to update the time (every second)
        current_time = time.time()
        if current_time - last_time_update >= 2.0:
            pr.print_status_bar(stdscr)
            last_time_update = current_time
            
        if should_repaint:
            tsk.reassign_task_ids(st.filtered_tasks)
            if st.searching and not st.focus_manager.is_tasks_focused(): 
                st.focus_manager.toggle_focus()
            if st.focus_manager.is_tasks_focused():
                if st.task_cnt > 0:
                    if st.current_task_id > st.task_cnt:
                        st.current_task_id = st.task_cnt
                        st.current_task_row = min(st.current_task_row, st.latest_max_capacity)
                    
                    # Render the whole view
                    pr.print_whole_view(stdscr, categories, sidebar_scroller.start_index)
                    
                else:
                    pr.print_whole_view(stdscr, categories, sidebar_scroller.start_index)
            else:
                pr.print_whole_view(stdscr, categories, sidebar_scroller.start_index)
            if st.searching:
                pr.print_q_to_close(stdscr, "search")
            should_repaint = False
            stdscr.refresh()
            
        # Wait for user input
        key = stdscr.getch()
                
        if key == -1:
            continue
            
        if key == kc.TAB:
            if st.searching:
                continue
            st.focus_manager.toggle_focus()
            should_repaint = True
            continue
            
        if key == curses.KEY_MOUSE:
            try:
                _, mouse_x, mouse_y, _, button_state = curses.getmouse()
                
                if button_state & curses.BUTTON4_PRESSED:  # Scroll up
                    if st.focus_manager.is_sidebar_focused():
                        task_scroll_offset = 0
                        sidebar_scroller.scroll_up()
                        if len(categories) > 0:
                            st.current_category_id = categories[sidebar_scroller.current_index]["id"]
                            _restore_state(task_list)
                        should_repaint = True
                    elif st.task_cnt > 0:
                        task_scroll_offset = 0
                        should_repaint = nv.keyup_update(True)
                    continue
            
                elif button_state & curses.BUTTON5_PRESSED:  # Scroll down
                    if st.focus_manager.is_sidebar_focused():
                        task_scroll_offset = 0
                        sidebar_scroller.scroll_down()
                        if len(categories) > 0:
                            st.current_category_id = categories[sidebar_scroller.current_index]["id"]
                            _restore_state(task_list)
                        should_repaint = True
                    elif st.task_cnt > 0:
                        task_scroll_offset = 0
                        should_repaint = nv.keydown_update(True)
                    continue

                elif mouse_x < cat.SIDEBAR_WIDTH and button_state & curses.BUTTON1_PRESSED:
                    if st.searching:
                        continue
                    if not st.focus_manager.is_sidebar_focused():
                        st.focus_manager.toggle_focus()
                        should_repaint = True
                    
                    if 1 <= mouse_y <= min(len(categories), st.latest_max_capacity):
                        clicked_cat_index = sidebar_scroller.start_index + mouse_y - 1
                        
                        if 0 <= clicked_cat_index < len(categories):
                            old_category_id = st.current_category_id
                            sidebar_scroller.current_index = clicked_cat_index
                            st.current_category_id = categories[clicked_cat_index]["id"]
                            
                            if old_category_id != st.current_category_id:
                                _restore_state(task_list)
                                should_repaint = True
                    continue
                
                if mouse_x >= cat.SIDEBAR_WIDTH and button_state & curses.BUTTON1_PRESSED:
                    if not st.focus_manager.is_tasks_focused():
                        st.focus_manager.toggle_focus()
                        should_repaint = True
                    
                    # Only handle task selection if clicked on a valid task row
                    if 1 <= mouse_y <= min(st.task_cnt, st.latest_max_capacity):
                        clicked_task_id = st.start_task_id + mouse_y - 1
                        clicked_task_row = mouse_y  # Row on screen
                        
                        if st.start_task_id <= clicked_task_id <= st.end_task_id:
                            task_index = clicked_task_id - 1
                            
                            flag_x_start = cat.SIDEBAR_WIDTH + 3
                            flag_x_end = flag_x_start + 1 
                            
                            status_x_start = cat.SIDEBAR_WIDTH + 5
                            status_x_end = status_x_start + 1

                            if flag_x_start <= mouse_x <= flag_x_end:
                                if st.filtered_tasks:
                                    tsk.flip_by_key(task_index, "flagged", task_list)
                            elif status_x_start <= mouse_x <= status_x_end:
                                if st.filtered_tasks:
                                    tsk.flip_by_key(task_index, "status", task_list)
                            else:
                                st.current_task_id = clicked_task_id
                                st.current_task_row = clicked_task_row
                            should_repaint = True
            except curses.error:
                # getmouse() can raise an exception if the terminal doesn't support mouse
                pass
            continue
        
        if key == ord('q'):
            if st.searching:
                _quit_search(stdscr, task_list)
                should_repaint = True
                continue
            break
        if key == ord(':'):
            command = _handle_command_input(stdscr)
            if command == "":
                pr.clear_bottom_bar_except_status(stdscr)    
                continue
            task_list, cats = cmd.execute_command(stdscr, command, task_list)
            pr.clear_bottom_bar_except_status(stdscr)
            # Check if we have newly loaded categories in the result (special case for dev/restore)
            if cats is not None:
                categories = _handle_dev_restore(cats, task_list, sidebar_scroller)
            should_repaint = True
        
        if key == ord('/'):
            query = ""
            curses.curs_set(1)
            stdscr.timeout(-1)  # Blocking input for search
            pr.clear_bottom_bar_except_status(stdscr)
            sf.safe_addstr(stdscr, st.latest_max_y - 2, 1, "/")
            
            while True:
                ch = stdscr.getch()
                
                if ch == kc.ENTER:
                    break
                    
                elif ch == kc.ESC:
                    query = ""
                    break
                    
                elif ch == kc.BACKSPACE or ch == curses.KEY_BACKSPACE:                    
                    if query:
                        query = query[:-1]
                        pr.clear_bottom_bar_except_status(stdscr)
                        sf.safe_addstr(stdscr, st.latest_max_y - 2, 1, f"/{query}")
                
                elif 32 <= ch <= 126:
                    query += chr(ch)
                    sf.safe_addstr(stdscr, st.latest_max_y - 2, len(query) + 1, chr(ch))
                
                if query:
                    st.filtered_tasks = srch.search(query, task_list)
                    st.searching = True
                    st.task_cnt = len(st.filtered_tasks)
                    
                    if st.task_cnt > 0:
                        st.current_task_id = 1
                        st.current_task_row = 1
                        st.start_task_id = 1
                        st.end_task_id = min(st.latest_max_capacity, st.task_cnt)
                    
                    pr.clear_task_panel(stdscr)
                    _sort_by_flagged_done_tag(categories)
                    pr.print_task_entries(stdscr, cat.SIDEBAR_WIDTH)
                    sf.safe_move(stdscr, st.latest_max_y - 2, len(query) + 2)
                    stdscr.refresh()
                else:
                    _restore_task_panel(task_list, categories)
                    pr.clear_task_panel(stdscr)
                    pr.print_task_entries(stdscr, cat.SIDEBAR_WIDTH)
                    sf.safe_move(stdscr, st.latest_max_y - 2, 2)
                    stdscr.refresh()
            
            stdscr.timeout(500)
            curses.curs_set(0)
            
            if query == "":
                _quit_search(stdscr, task_list)
            
            should_repaint = True
        
        if st.focus_manager.is_sidebar_focused():
            if key == curses.KEY_UP:
                task_scroll_offset = 0
                sidebar_scroller.scroll_up()
                if len(categories) > 0:
                    st.current_category_id = categories[sidebar_scroller.current_index]["id"]
                    _restore_state(task_list)
                should_repaint = True
                
            elif key == curses.KEY_DOWN:
                task_scroll_offset = 0
                sidebar_scroller.scroll_down()
                if len(categories) > 0:
                    st.current_category_id = categories[sidebar_scroller.current_index]["id"]
                    _restore_state(task_list)
                should_repaint = True

            elif key == ord('a'):
                if st.searching:
                    continue
                cat_count = len(categories)
                visible_count = min(cat_count, st.latest_max_capacity)
                is_sidebar_full = visible_count >= st.latest_max_capacity
                if is_sidebar_full:
                    # scroll up
                    sidebar_scroller.start_index = cat_count - st.latest_max_capacity + 1
                    new_cat_row = st.latest_max_capacity
                else:
                    new_cat_row = visible_count + 1
                    
                new_cat_id = max([c["id"] for c in categories], default=0) + 1
                temp_category = {
                    "id": new_cat_id, 
                    "name": ""
                }
                old_cat_id = st.current_category_id
                st.current_category_id = new_cat_id
                
                pr.print_category_entries(stdscr, categories, sidebar_scroller.start_index)
                sf.safe_move(stdscr, new_cat_row, 1)  # 1-space indent, matching print_category()
                
                new_cat_name = ed.edit(stdscr, temp_category, "name", pr.add_mode, 0)
                temp_category["name"] = new_cat_name
                
                if new_cat_name != "":
                    # Enforce maximum length for category name
                    if len(new_cat_name) > cat.MAX_CATEGORY_NAME_LENGTH:
                        new_cat_name = new_cat_name[:cat.MAX_CATEGORY_NAME_LENGTH]
                        
                    new_cat = cat.add_category(new_cat_name)
                    if new_cat:
                        # Reload categories and update scroller
                        categories = cat.load_categories()
                        sidebar_scroller.update_total(len(categories))
                        
                        # Find and select the new category
                        for i, c in enumerate(categories):
                            if c["id"] == new_cat["id"]:
                                sidebar_scroller.current_index = i
                                st.current_category_id = new_cat["id"]
                                break
                                
                        # Update filtered tasks for the new category
                        _restore_state(task_list)
                        st.cat_cnt = len(categories)
                        pr.print_msg_in_task_panel(stdscr, msg.EMPTY_MSG, cat.SIDEBAR_WIDTH)
                else:
                    st.current_category_id = old_cat_id
                    should_repaint = True

            elif key == ord('e'):
                # Edit category name with scrolling (skip for "All Tasks" category)
                if len(categories) > 0 and st.current_category_id != 0:
                    # Get current category to edit
                    current_cat = categories[sidebar_scroller.current_index]
                    row = sidebar_scroller.current_index - sidebar_scroller.start_index + 1
                    sf.safe_move(stdscr, row, 0)
                    
                    # Create a temporary copy for editing using the same mechanism as tasks
                    edit_cat = current_cat.copy()                    
                    new_name = ed.edit(stdscr, edit_cat, "name", pr.edit_mode, 0)
                    
                    if new_name:
                        # Enforce maximum length for category name
                        if len(new_name) > cat.MAX_CATEGORY_NAME_LENGTH:
                            new_name = new_name[:cat.MAX_CATEGORY_NAME_LENGTH]
                        cat.update_category_name(st.current_category_id, new_name)
                        categories = cat.load_categories()
                    
                    should_repaint = True
            
            elif key == curses.KEY_BACKSPACE or key == kc.BACKSPACE:
                # Delete selected category (with double backspace confirmation)
                if len(categories) > 0 and st.current_category_id != 0:
                    # Wait for confirmation
                    k = stdscr.getch()
                    if k == curses.KEY_BACKSPACE or k == kc.BACKSPACE:
                        
                        # Handle tasks in this category
                        task_list = [task for task in task_list if task.get("category_id", 0) != st.current_category_id]
                        tsk.reassign_task_ids(task_list)
                        tsk.save_tasks(task_list)
                        cat.delete_category(st.current_category_id)
                        categories = cat.reassign_category_ids()
                        
                        for task in task_list:
                            if task["category_id"] > st.current_category_id:
                                task["category_id"] -= 1
                        tsk.save_tasks(task_list)
                        
                        # A category in the middle might be deleted
                        if len(categories) > 1:
                            # We need to reload tasks after renumbering to ensure proper associations
                            task_list = tsk.load_tasks()
                        
                        sidebar_scroller.update_total(len(categories))
                        
                        # Only category id if the last category was deleted
                        if len(categories) == st.current_category_id:
                            new_index = st.current_category_id - 1
                            sidebar_scroller.current_index = new_index
                            st.current_category_id = categories[new_index]["id"]

                        _restore_state(task_list)
                    
                    should_repaint = True
                
        elif st.focus_manager.is_tasks_focused():
            if key == ord('a'):
                if st.searching:
                    continue
                if st.task_cnt == tsk.MAX_TASK_COUNT:
                    pr.print_msg(stdscr, msg.limit_msg)
                    time.sleep(1.2)
                    continue
                
                # Store old values for potential rollback
                old_start = st.start_task_id
                old_end = st.end_task_id
                
                # adjust start end for pre-print
                # taskoverflow if a new one is added:
                if st.task_cnt >= st.latest_max_capacity and st.end_task_id <= st.task_cnt:
                    st.start_task_id = st.task_cnt - (st.end_task_id - st.start_task_id - 1)
                    st.end_task_id = st.task_cnt

                st.adding_task = True
                
                pr.clear_task_panel(stdscr)
                pr.print_task_entries(stdscr, cat.SIDEBAR_WIDTH)

                # Add a new task with proper indentation
                new_task_id = f"{st.task_cnt + 1:2d}"
                y_pos = st.latest_max_capacity if st.task_cnt >= st.latest_max_capacity else st.task_cnt + 1
                sf.safe_addstr(stdscr, y_pos, cat.SIDEBAR_WIDTH, f"{new_task_id} ")

                # Move cursor to the correct position after task number
                sf.safe_move(stdscr, y_pos, cat.SIDEBAR_WIDTH + tsk.TASK_INDENT_IN_TASK_PANEL)
                new_task = tsk.create_new_task(st.task_cnt + 1)
                new_task["category_id"] = 0 if st.current_category_id == 0 else st.current_category_id
                
                new_task_description = ed.edit(stdscr, new_task, "description", pr.add_mode)  
                if new_task_description != "":
                    st.current_task_id = st.task_cnt + 1
                st.adding_task = False
                
                if new_task_description != "":
                    new_id = st.task_cnt + 1
                    due_date, new_task_description = due.parse_due_date(new_task_description)
                    if new_task_description != "":
                        task_list = tsk.add_new_task(
                            task_list, new_id, new_task_description, False, new_task["category_id"], due_date)
                        st.task_cnt = st.task_cnt + 1
                        st.filtered_tasks = tsk.get_tasks_by_category_id(task_list, st.current_category_id)
                        
                        if st.task_cnt == 1:
                            st.start_task_id = 1
                        if st.task_cnt - 1 <= st.latest_max_capacity:
                            st.current_task_row = st.task_cnt
                        else:
                            st.current_task_row = st.latest_max_capacity
                        st.current_task_id = new_id
                        st.end_task_id = st.end_task_id + 1
                        task_scroll_offset = 0
                else:
                    st.start_task_id = old_start
                    st.end_task_id = old_end
                    
                should_repaint = True
                
            elif key == ord('d') or key == ord(' '):
                if st.filtered_tasks and st.current_task_id > 0:
                    task_idx = st.current_task_id - 1
                    tsk.flip_by_key(task_idx, "status", task_list)
                    should_repaint = True
                    
            elif key == ord('e'):
                if st.task_cnt > 0 and st.current_task_id > 0:
                    task_list = ed.handle_edit(stdscr, task_list)
                    should_repaint = True
                
            elif key == ord('f'):
                if st.filtered_tasks and st.current_task_id > 0:
                    task_idx = st.current_task_id - 1
                    tsk.flip_by_key(task_idx, "flagged", task_list)
                    should_repaint = True
                    
            elif key == curses.KEY_RIGHT:
                right_frame_pos = st.latest_max_x - 1
                base_indent = tsk.TASK_INDENT_IN_TASK_PANEL
                text_start_pos = cat.SIDEBAR_WIDTH + base_indent
                current_task = st.filtered_tasks[st.current_task_id - 1]
                date_length = len(current_task["due"])
                date_pos = right_frame_pos - date_length - 1  # Only 1 char gap from right frame
                max_visible_width = date_pos - text_start_pos - 1
                if len(current_task["description"]) > max_visible_width and task_scroll_offset < len(current_task["description"]) - max_visible_width:
                    task_scroll_offset += 1
                    pr.print_editing_entry(stdscr, current_task, "description", st.current_task_row, True, task_scroll_offset) 
                
            elif key == curses.KEY_LEFT:
                old_task_scroll_offset = task_scroll_offset
                task_scroll_offset = max(0, task_scroll_offset - 1)
                if task_scroll_offset >= 0 and old_task_scroll_offset > task_scroll_offset:
                    pr.print_editing_entry(stdscr, st.filtered_tasks[st.current_task_id - 1], "description", st.current_task_row, True, task_scroll_offset)
                
            elif key == curses.KEY_UP:
                task_scroll_offset = 0
                if st.task_cnt > 0:
                    should_repaint = nv.keyup_update(True)
                    
            elif key == curses.KEY_DOWN:
                task_scroll_offset = 0
                if st.task_cnt > 0:
                    should_repaint = nv.keydown_update(True)
                
            elif key == curses.KEY_BACKSPACE or key == kc.BACKSPACE:
                second_key = stdscr.getch()
                if second_key == curses.KEY_BACKSPACE or second_key == kc.BACKSPACE:
                    if len(st.filtered_tasks) > 0:
                        task_list = cmd.handle_delete(task_list)
                    tsk.save_tasks(task_list)
                    should_repaint = True

def run():
    import todoism.cli as cli
    cli.run()
    