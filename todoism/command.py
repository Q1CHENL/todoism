import curses
import copy
import time

import todoism.task as tsk
import todoism.edit as ed
import todoism.print as pr
import todoism.message as msg
import todoism.preference as pref
import todoism.navigate as nv
import todoism.color as clr
import todoism.strikethrough as stk
import todoism.keycode as kc
import todoism.category as cat
import todoism.state as st

def purge(task_list, purged_list):
    """
    purge completed tasks
    """
    remained = []
    for t in task_list:
        if t['status'] is False:
            remained.append(t)
        else:
            purged_list.append(t)
    tsk.reassign_task_ids(remained)
    tsk.save_tasks(purged_list, pref.purged_file_path)
    return remained, []


def sort(task_list, key) -> list:
    marked = []
    not_marked = []
    for t in task_list:
        if t[key] is True:
            marked.append(t)
        else:
            not_marked.append(t)
    return marked + not_marked


def execute_command(
        stdscr, 
        command, 
        task_list, 
        done_list, 
        purged_list,
        ):
    command_recognized = False    
    if command.startswith("done "):
        tasks_sperated_by_comma = command[5:].split(' ')
        if len(tasks_sperated_by_comma) == 1:
            ids_to_done = tasks_sperated_by_comma[0].split(',')
            if all(i.isdigit() for i in ids_to_done):
                for id_to_done in ids_to_done:
                    index_to_done = int(id_to_done) - 1
                    if 0 <= index_to_done < len(task_list):
                        done_list.append(copy.copy(task_list[index_to_done]))
                        task_uuid = st.filtered_tasks[index_to_done].get('uuid')
                        tsk.done_task_by_uuid(task_list, task_uuid)
        command_recognized = True
    elif command.startswith("flag "):
        tasks_sperated_by_comma = command[5:].split(' ')
        if len(tasks_sperated_by_comma) == 1:
            ids_to_flag = tasks_sperated_by_comma[0].split(',')
            if all(i.isdigit() for i in ids_to_flag):
                for id_to_flag in ids_to_flag:
                    index_to_flag = int(id_to_flag) - 1
                    if 0 <= index_to_flag < len(task_list):
                        tsk.flag_task_by_uuid(task_list, task_list[index_to_flag]['uuid'])
        command_recognized = True
    elif command == "purge":
        original_cnt = len(task_list)
        displayed_task_cnt = st.end_task_id - st.start_task_id + 1
        task_list, done_list = purge(task_list, purged_list)
        tsk.save_tasks(task_list)
        # change current id to 1 if some tasks were purged
        if len(task_list) < original_cnt:
            # temporary solution: back to top
            st.current_task_id = 1
            st.current_task_row = 1
            st.start_task_id = 1
            if len(task_list) > displayed_task_cnt:
                st.end_task_id = displayed_task_cnt
            else:
                st.end_task_id = len(task_list)
        command_recognized = True
    elif command.startswith("del "):
        parts = command.split()
        if len(parts) > 1 and parts[1].isdigit():
            task_id = int(parts[1])
            if 1 <= task_id <= len(task_list):
                task_uuid = task_list[task_id - 1].get('uuid')
                task_list = tsk.delete_task_by_uuid(task_list, task_uuid)
                # Update current_task_id, current_task_row, start, end after deletion
                nv.post_deletion_update(len(task_list))
        command_recognized = True
    elif command.startswith("edit "):
        task_id = command[5:]
        if task_id.isdigit() and int(task_id) <= len(task_list):
            st.latest_max_capacity = stdscr.getmaxyx()[0] - 1    
            edit_id = int(task_id)

            curses.echo()
            curses.curs_set(1)
            st.current_task_row = edit_id - st.start_task_id + 1
            if len(task_list) and edit_id >= st.start_task_id and edit_id <= st.end_task_id:
                st.current_task_id, st.current_task_row, st.start_task_id, st.end_task_id = ed.edit_and_save(
                    stdscr, 
                    task_list, 
                    edit_id,
                    st.current_task_row,
                    st.start_task_id,
                    st.end_task_id,
                    edit_id - st.start_task_id + 1,
                    len(task_list[edit_id - 1]['description']) + tsk.TASK_INDENT_IN_TASK_PANEL,
                    st.latest_max_capacity
                )
            curses.curs_set(0)
            curses.noecho()      
        command_recognized = True
    elif command == "help":
        open_help_page(stdscr)
        st.old_max_x = st.latest_max_x
        st.old_max_y = st.latest_max_y
        old_timeout = 500
        stdscr.timeout(-1)
        while True:
            st.latest_max_y, st.latest_max_x = stdscr.getmaxyx()
            if st.latest_max_x != st.old_max_x or st.latest_max_y != st.old_max_y:
                st.old_max_x = st.latest_max_x
                st.old_max_y = st.latest_max_y
                open_help_page(stdscr)

            ch = stdscr.getch()
            if ch == ord('q'):
                break
        stdscr.timeout(old_timeout)
        return task_list, done_list
    elif command == "pref":
        selection_index = 0
        open_pref_panel(stdscr, selection_index)
        command_recognized = True
        old_timeout = 500  
        stdscr.timeout(-1)
        quit = False
        
        st.old_max_x = st.latest_max_x
        st.old_max_y = st.latest_max_y
        
        while True:
            if quit:
                break                
            # Keep selection index in valid range
            if selection_index > 10:
                selection_index = 10
            elif selection_index < 0:
                selection_index = 0
            st.latest_max_y, st.latest_max_x = stdscr.getmaxyx()
            if st.latest_max_x != st.old_max_x or st.latest_max_y != st.old_max_y:
                st.old_max_x = st.latest_max_x
                st.old_max_y = st.latest_max_y
                open_pref_panel(stdscr, selection_index)
                        
            # Display the preference panel with current selection
            pr.print_pref_panel(stdscr, selection_index)
            
            # Get the current preference item
            line = msg.pref_panel.strip().split('\n')[selection_index + 2].strip().split(':')
            preference_type = line[0].strip()
            
            # Handle different preference types
            if preference_type == "│   Tag":
                ch = stdscr.getch()
                if ch == kc.TAB:
                    # Toggle Tag setting
                    pref.set_tag(not pref.get_tag())
                    # Refresh to show the change
                    pr.print_pref_panel(stdscr, selection_index)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            
            elif preference_type == "│   Strikethrough":
                ch = stdscr.getch()
                if ch == kc.TAB:
                    # Toggle strikethrough setting
                    stk.set_strikethrough(not stk.get_strikethrough())
                    # Refresh to show the change
                    pr.print_pref_panel(stdscr, selection_index)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            
            elif preference_type == "│   Color":
                # Get currently selected color
                colors = ["blue", "red", "yellow", "green"]
                current_color = clr.get_theme_color_str()
                color_index = colors.index(current_color) if current_color in colors else 0
                
                ch = stdscr.getch()
                if ch == kc.TAB:
                    # Cycle through colors
                    color_index = (color_index + 1) % len(colors)
                    clr.set_theme_color(colors[color_index])
                    # Refresh to show the change
                    pr.print_pref_panel(stdscr, selection_index)
                    # Update color pair for selection
                    curses.init_pair(9, curses.COLOR_BLACK, clr.get_theme_color_curses())
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            
            elif preference_type == "│   Date format":
                ch = stdscr.getch()
                if ch == kc.TAB:
                    # Get current date format and cycle through options
                    date_formats = ["Y-M-D", "D-M-Y", "M-D-Y"]
                    current_format = pref.get_date_format()
                    date_index = date_formats.index(current_format) if current_format in date_formats else 0
                    date_index = (date_index + 1) % len(date_formats)
                    pref.set_date_format(date_formats[date_index])
                    # Refresh to show the change
                    pr.print_pref_panel(stdscr, selection_index)
                    tsk.update_all_task_date_format(task_list, current_format)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            
            elif preference_type.startswith("│   Sort by flagged"):
                ch = stdscr.getch()
                if ch == kc.TAB:
                    pref.set_sort_flagged(not pref.get_sort_flagged())
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            elif preference_type.startswith("│   Sort by done"):
                ch = stdscr.getch()
                if ch == kc.TAB:
                    pref.set_sort_done(not pref.get_sort_done())
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            # Handle any other preference types or empty lines
            else:
                ch = stdscr.getch()
                if ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
        
        # Restore original timeout
        stdscr.timeout(old_timeout)
    elif command.startswith("tag "):
        tag = command[4:]
        if tag == "on":
            pref.set_tag(True)
            command_recognized = True
        elif tag == "off":
            pref.set_tag(False)
            command_recognized = True
    elif command == 'dev':
        # Hidden command for developers - load test data
        try:
            import test.test as test_module
            
            if test_module.is_dev_mode_active():
                max_y, max_x = stdscr.getmaxyx()
                sidebar_width = 16
                warning_msg = "Already in dev mode!"
                stdscr.move(st.latest_max_capacity, sidebar_width)
                stdscr.clrtoeol()
                yellow_pair_num = clr.get_color_pair_num_by_str_text("yellow")
                stdscr.attron(curses.color_pair(yellow_pair_num) | curses.A_BOLD)
                stdscr.addstr(st.latest_max_capacity, sidebar_width, warning_msg)
                stdscr.attroff(curses.color_pair(yellow_pair_num) | curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                stdscr.move(st.latest_max_capacity, sidebar_width)
                stdscr.clrtoeol()
            else:
                if test_module.load_dev_mode():
                    task_list = tsk.load_tasks()
                    categories = cat.load_categories()
                    st.current_category_id = 0
                    
                    # Reset view
                    st.current_task_id = 1
                    st.current_task_row = 1
                    st.start_task_id = 1
                    st.end_task_id = min(len(task_list), st.latest_max_capacity)
                    
                    # Show success message
                    max_y, max_x = stdscr.getmaxyx()
                    sidebar_width = 16
                    success_msg = "Dev mode enabled. Test tasks and categories loaded. Will auto-restore on exit."
                    stdscr.move(st.latest_max_capacity, sidebar_width)
                    stdscr.clrtoeol()
                    green_pair_num = clr.get_color_pair_num_by_str_text("green")
                    stdscr.attron(curses.color_pair(green_pair_num) | curses.A_BOLD)
                    stdscr.addstr(st.latest_max_capacity, sidebar_width, success_msg)
                    stdscr.attroff(curses.color_pair(green_pair_num) | curses.A_BOLD)
                    stdscr.refresh()
                    time.sleep(1.5)
                    stdscr.move(st.latest_max_capacity, sidebar_width)
                    stdscr.clrtoeol()
                    
                    # Return updated categories and category ID
                    return task_list, done_list, categories
        except ImportError:
            # Test module not found (likely PyPI installation)
            max_y, max_x = stdscr.getmaxyx()
            sidebar_width = 16
            warning_msg = "Dev mode not available in installation."
            stdscr.move(st.latest_max_capacity, sidebar_width)
            stdscr.clrtoeol()
            yellow_pair_num = clr.get_color_pair_num_by_str_text("yellow")
            stdscr.attron(curses.color_pair(yellow_pair_num) | curses.A_BOLD)
            stdscr.addstr(st.latest_max_capacity, sidebar_width, warning_msg)
            stdscr.attroff(curses.color_pair(yellow_pair_num) | curses.A_BOLD)
            stdscr.refresh()
            time.sleep(1.5)
            stdscr.move(st.latest_max_capacity, sidebar_width)
            stdscr.clrtoeol()
        command_recognized = True
        
    elif command == "restore":
        # Hidden command for developers - restore real data
        try:
            import test.test as test_module
            
            if not test_module.is_dev_mode_active():
                max_y, max_x = stdscr.getmaxyx()
                sidebar_width = 16
                warning_msg = "Not in dev mode - nothing to restore!"
                stdscr.move(st.latest_max_capacity, sidebar_width)
                stdscr.clrtoeol()
                yellow_pair_num = clr.get_color_pair_num_by_str_text("yellow")
                stdscr.attron(curses.color_pair(yellow_pair_num) | curses.A_BOLD)
                stdscr.addstr(st.latest_max_capacity, sidebar_width, warning_msg)
                stdscr.attroff(curses.color_pair(yellow_pair_num) | curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                stdscr.move(st.latest_max_capacity, sidebar_width)
                stdscr.clrtoeol()
            else:
                if test_module.exit_dev_mode():
                    task_list = tsk.load_tasks()
                    categories = cat.load_categories()
                    st.current_category_id = 0
                    
                    # Reset view
                    st.current_task_id = 1 if len(task_list) > 0 else 0
                    st.current_task_row = 1 if len(task_list) > 0 else 0
                    st.start_task_id = 1 if len(task_list) > 0 else 0
                    st.end_task_id = min(len(task_list), st.latest_max_capacity) if len(task_list) > 0 else 0
                    
                    # Show success message
                    max_y, max_x = stdscr.getmaxyx()
                    sidebar_width = 16
                    success_msg = "Dev mode disabled. Original tasks and categories restored."
                    stdscr.move(st.latest_max_capacity, sidebar_width)
                    stdscr.clrtoeol()
                    green_pair_num = clr.get_color_pair_num_by_str_text("green")
                    stdscr.attron(curses.color_pair(green_pair_num) | curses.A_BOLD)
                    stdscr.addstr(st.latest_max_capacity, sidebar_width, success_msg)
                    stdscr.attroff(curses.color_pair(green_pair_num) | curses.A_BOLD)
                    stdscr.refresh()
                    time.sleep(1.5)
                    stdscr.move(st.latest_max_capacity, sidebar_width)
                    stdscr.clrtoeol()
                    
                    # Return updated categories and category ID
                    return task_list, done_list, categories
        except ImportError:
            # Test module not found (likely PyPI installation)
            max_y, max_x = stdscr.getmaxyx()
            sidebar_width = 16
            warning_msg = "Dev mode not available in installation"
            stdscr.move(st.latest_max_capacity, sidebar_width)
            stdscr.clrtoeol()
            yellow_pair_num = clr.get_color_pair_num_by_str_text("yellow")
            stdscr.attron(curses.color_pair(yellow_pair_num) | curses.A_BOLD)
            stdscr.addstr(st.latest_max_capacity, sidebar_width, warning_msg)
            stdscr.attroff(curses.color_pair(yellow_pair_num) | curses.A_BOLD)
            stdscr.refresh()
            time.sleep(1.5)
            stdscr.move(st.latest_max_capacity, sidebar_width)
            stdscr.clrtoeol()
        command_recognized = True
        
    elif command.strip() == "":
        command_recognized = True

    if not command_recognized and command.strip():
        max_y, max_x = stdscr.getmaxyx()
        sidebar_width = 16
        error_msg = f"Invalid command: '{command}'. Type command 'help' for help."
        
        # Clear the line first
        stdscr.move(st.latest_max_capacity, sidebar_width)
        stdscr.clrtoeol()
        
        red_pair_num = clr.get_color_pair_num_by_str_text("red")
        stdscr.attron(curses.color_pair(red_pair_num) | curses.A_BOLD)
        stdscr.addstr(st.latest_max_capacity, sidebar_width, error_msg)
        stdscr.attroff(curses.color_pair(red_pair_num) | curses.A_BOLD)
        stdscr.refresh()
        
        time.sleep(1.5)
        
        # Clear the error message
        stdscr.move(st.latest_max_capacity, sidebar_width)
        stdscr.clrtoeol()
        stdscr.refresh()
    
    return task_list, done_list

def open_help_page(stdscr):
    stdscr.clear()
    pr.print_outer_frame(stdscr)
    pr.print_msg(stdscr, msg.help_msg)
    pr.print_q_to_close(stdscr, "help", st.latest_max_x, st.latest_max_y)

def open_pref_panel(stdscr, selection_index):
    stdscr.clear()
    pr.print_pref_panel(stdscr, selection_index)
    pr.print_outer_frame(stdscr)
    pr.print_q_to_close(stdscr, "preferences", st.latest_max_x, st.latest_max_y)