import curses
import copy
import time

import todoism.task as tsk
import todoism.edit as ed
import todoism.print as pr
import todoism.settings as st
import todoism.category as cat
import todoism.navigate as nv


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
    tsk.save_tasks(purged_list, tsk.purged_file_path)
    return remained, []


def sort(task_list, key):
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
        filtered_tasks,
        done_list, 
        purged_list,
        current_id,
        start,
        end,
        current_row,
        max_capacity
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
                        task_uuid = filtered_tasks[index_to_done].get('uuid')
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
        displayed_task_cnt = end - start + 1
        task_list, done_list = purge(task_list, purged_list)
        tsk.save_tasks(task_list, tsk.tasks_file_path)
        # change current id to 1 if some tasks were purged
        if len(task_list) < original_cnt:
            # temporary solution: back to top
            current_id = 1
            current_row = 1
            start = 1
            if len(task_list) > displayed_task_cnt:
                end = displayed_task_cnt
            else:
                end = len(task_list)
        command_recognized = True
    elif command == "purge all":
        task_list = []
        tsk.save_tasks(task_list, tsk.tasks_file_path)
        command_recognized = True
    elif command.startswith("sort "):
        category = command[5:]
        if category == 'f':
            task_list = sort(task_list, "flagged")
            tsk.reassign_task_ids(task_list)
            command_recognized = True
        elif category == 'd':
            task_list = sort(task_list, "status")
            tsk.reassign_task_ids(task_list)
            command_recognized = True
    elif command == "group":
        command_recognized = True
    elif command.startswith("color "):
        st.set_color_selected(command[6:])
        command_recognized = True
    elif command == "help":
        max_y, max_x = stdscr.getmaxyx()
        pr.print_msg(stdscr, pr.help_msg)
        hint = "┤Press 'q' to close help├"
        hint_pos_x = (max_x - 15) // 2 + 15 - len(hint) // 2
        stdscr.addstr(max_y - 1, hint_pos_x, hint)
        stdscr.refresh()
        
        old_timeout = 500
        stdscr.timeout(-1)
        while True:
            ch = stdscr.getch()
            if ch == ord('q') or ch == 27:  # 'q' or ESC
                break
        stdscr.timeout(old_timeout)
        return task_list, done_list, current_id, current_row, start, end
    elif command.startswith("del "):
        parts = command.split()
        if len(parts) > 1 and parts[1].isdigit():
            task_id = int(parts[1])
            if 1 <= task_id <= len(task_list):
                task_uuid = task_list[task_id - 1].get('uuid')
                task_list = tsk.delete_task_by_uuid(task_list, task_uuid)
                # Update current_id, current_row, start, end after deletion
                current_id, current_row, start, end = nv.post_deletion_update(
                    current_id, current_row, start, end, len(task_list), max_capacity
                )
        command_recognized = True
    elif command.startswith("edit "):
        task_id = command[5:]
        if task_id.isdigit() and int(task_id) <= len(task_list):
            max_capacity = stdscr.getmaxyx()[0] - 1    
            edit_id = int(task_id)
            
            categories = cat.load_categories()
            done_cnt = tsk.done_count(task_list)            
            current_category_id = 0
            pr.print_main_view_with_sidebar(
                stdscr,
                done_cnt,
                len(task_list),
                task_list,
                edit_id,
                start,
                end,
                categories,
                current_category_id,
                0,  # Start at first category 
                False  # Tasks have focus
            )
            
            curses.echo()
            curses.curs_set(1)
            current_row = edit_id - start + 1
            if len(task_list) and edit_id >= start and edit_id <= end:
                current_id, current_row, start, end = ed.edit_and_save(
                    stdscr, 
                    task_list, 
                    edit_id,
                    current_row,
                    start,
                    end,
                    edit_id - start + 1,
                    len(task_list[edit_id - 1]['description']) + ed.indent,
                    max_capacity
                )
            curses.curs_set(0)
            curses.noecho()      
        command_recognized = True
    elif command.startswith("st "):
        option = command[4:]
        if option == "on":
            st.set_strikethrough(True)
        elif option == "off":
            st.set_strikethrough(False)
        
        categories = cat.load_categories()
        done_cnt = tsk.done_count(task_list)
        current_category_id = 0
        pr.print_main_view_with_sidebar(
            stdscr,
            done_cnt,
            len(task_list),
            task_list,
            current_id,
            start,
            end,
            categories,
            current_category_id,
            0,  # Start at first category 
            False  # Tasks have focus
        )
        command_recognized = True
    elif command == "test":
        # Hidden command for developers - load test data
        try:
            import test.test as test_module
            import todoism.category as cat
            
            if test_module.is_test_mode_active():
                max_y, max_x = stdscr.getmaxyx()
                sidebar_width = 16
                warning_msg = "Already in test mode!"
                stdscr.move(max_capacity, sidebar_width)
                stdscr.clrtoeol()
                stdscr.attron(curses.color_pair(3) | curses.A_BOLD)  # Yellow
                stdscr.addstr(max_capacity, sidebar_width, warning_msg)
                stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                stdscr.move(max_capacity, sidebar_width)
                stdscr.clrtoeol()
            else:
                if test_module.load_test_mode():
                    task_list = tsk.load_tasks()
                    categories = cat.load_categories()
                    current_category_id = 0
                    
                    # Reset view
                    current_id = 1
                    current_row = 1
                    start = 1
                    end = min(len(task_list), max_capacity)
                    
                    # Show success message
                    max_y, max_x = stdscr.getmaxyx()
                    sidebar_width = 16
                    success_msg = "Test mode enabled. Test tasks and categories loaded. Will auto-restore on exit."
                    stdscr.move(max_capacity, sidebar_width)
                    stdscr.clrtoeol()
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)  # Green
                    stdscr.addstr(max_capacity, sidebar_width, success_msg)
                    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
                    stdscr.refresh()
                    time.sleep(1.5)
                    stdscr.move(max_capacity, sidebar_width)
                    stdscr.clrtoeol()
                    
                    # Return updated categories and category ID
                    return task_list, done_list, current_id, current_row, start, end, categories, current_category_id
        except ImportError:
            # Test module not found (likely PyPI installation)
            max_y, max_x = stdscr.getmaxyx()
            sidebar_width = 16
            warning_msg = "Test mode not available in installation"
            stdscr.move(max_capacity, sidebar_width)
            stdscr.clrtoeol()
            stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
            stdscr.addstr(max_capacity, sidebar_width, warning_msg)
            stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
            stdscr.refresh()
            time.sleep(1.5)
            stdscr.move(max_capacity, sidebar_width)
            stdscr.clrtoeol()
        command_recognized = True
        
    elif command == "restore":
        # Hidden command for developers - restore real data
        try:
            import test.test as test_module
            import todoism.category as cat
            
            if not test_module.is_test_mode_active():
                max_y, max_x = stdscr.getmaxyx()
                sidebar_width = 16
                warning_msg = "Not in test mode - nothing to restore!"
                stdscr.move(max_capacity, sidebar_width)
                stdscr.clrtoeol()
                stdscr.attron(curses.color_pair(3) | curses.A_BOLD)  # Yellow
                stdscr.addstr(max_capacity, sidebar_width, warning_msg)
                stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                stdscr.move(max_capacity, sidebar_width)
                stdscr.clrtoeol()
            else:
                if test_module.exit_test_mode():
                    task_list = tsk.load_tasks()
                    categories = cat.load_categories()
                    current_category_id = 0
                    
                    # Reset view
                    current_id = 1 if len(task_list) > 0 else 0
                    current_row = 1 if len(task_list) > 0 else 0
                    start = 1 if len(task_list) > 0 else 0
                    end = min(len(task_list), max_capacity) if len(task_list) > 0 else 0
                    
                    # Show success message
                    max_y, max_x = stdscr.getmaxyx()
                    sidebar_width = 16
                    success_msg = "Test mode disabled. Original tasks and categories restored."
                    stdscr.move(max_capacity, sidebar_width)
                    stdscr.clrtoeol()
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)  # Green
                    stdscr.addstr(max_capacity, sidebar_width, success_msg)
                    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
                    stdscr.refresh()
                    time.sleep(1.5)
                    stdscr.move(max_capacity, sidebar_width)
                    stdscr.clrtoeol()
                    
                    # Return updated categories and category ID
                    return task_list, done_list, current_id, current_row, start, end, categories, current_category_id
        except ImportError:
            # Test module not found (likely PyPI installation)
            max_y, max_x = stdscr.getmaxyx()
            sidebar_width = 16
            warning_msg = "Test mode not available in installation"
            stdscr.move(max_capacity, sidebar_width)
            stdscr.clrtoeol()
            stdscr.attron(curses.color_pair(3) | curses.A_BOLD)  # Yellow
            stdscr.addstr(max_capacity, sidebar_width, warning_msg)
            stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
            stdscr.refresh()
            time.sleep(1.5)
            stdscr.move(max_capacity, sidebar_width)
            stdscr.clrtoeol()
        command_recognized = True
        
    elif command.strip() == "":
        command_recognized = True

    if not command_recognized and command.strip():
        max_y, max_x = stdscr.getmaxyx()
        sidebar_width = 16
        error_msg = f"Invalid command: '{command}'. Type command 'help' for help."
        
        # Clear the line first
        stdscr.move(max_capacity, sidebar_width)
        stdscr.clrtoeol()
        
        stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(max_capacity, sidebar_width, error_msg)
        stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
        stdscr.refresh()
        
        time.sleep(1.35)
        
        # Clear the error message
        stdscr.move(max_capacity, sidebar_width)
        stdscr.clrtoeol()
        stdscr.refresh()
    
    return task_list, done_list, current_id, current_row, start, end

def execute_category_command(
        stdscr,
        command,
        categories,
        task_list,
        current_category_id
        ):
    """Execute category-related commands"""
    import todoism.category as cat
    
    if command.startswith("cadd "):
        category_name = command[5:]
        if category_name:
            # Enforce maximum length for category name
            if len(category_name) > cat.MAX_CATEGORY_NAME_LENGTH:
                category_name = category_name[:cat.MAX_CATEGORY_NAME_LENGTH]
                
            new_cat = cat.add_category(category_name)
            if new_cat:
                return categories + [new_cat], current_category_id
    elif command.startswith("cdel"):
        # Parse category ID to delete
        parts = command.split()
        if len(parts) > 1 and parts[1].isdigit():
            category_id = int(parts[1])
            # Don't allow deleting the "All" category
            if category_id != 0:
                # Handle tasks in this category
                for task in task_list:
                    if task.get('category_id', 0) == category_id:
                        # Move tasks to "All" category
                        task['category_id'] = 0
                
                # Delete the category
                success = cat.delete_category(category_id)
                if success:
                    # If we deleted the current category, go back to "All"
                    if current_category_id == category_id:
                        current_category_id = 0
                    
                    # Reload categories
                    categories = cat.load_categories()
                    tsk.save_tasks(task_list, tsk.tasks_file_path)
    elif command.startswith("cedit "):
        # Parse category ID and new name
        parts = command.split()
        if len(parts) >= 3:
            if parts[1].isdigit():
                category_id = int(parts[1])
                new_name = ' '.join(parts[2:])
                
                # Enforce maximum length for category name
                if len(new_name) > cat.MAX_CATEGORY_NAME_LENGTH:
                    new_name = new_name[:cat.MAX_CATEGORY_NAME_LENGTH]
                    
                success = cat.update_category_name(category_id, new_name)
                if success:
                    categories = cat.load_categories()
    elif command.startswith("ccolor "):
        # Parse category ID and color
        parts = command.split()
        if len(parts) == 3 and parts[1].isdigit():
            category_id = int(parts[1])
            color = parts[2]
            categories = cat.load_categories()
            for category in categories:
                if category['id'] == category_id:
                    category['color'] = color
                    cat.save_categories(categories)
                    break
    
    return categories, current_category_id


