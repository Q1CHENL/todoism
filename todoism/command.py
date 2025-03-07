import curses
import copy

import todoism.task as tsk
import todoism.utils as ut
import todoism.print as pr
import todoism.settings as st
import todoism.category as cat
import todoism.scroll as scr


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
        done_list, 
        purged_list,
        current_id,
        start,
        end,
        current_row,
        max_capacity
        ):
    if command.startswith("done "):
        tasks_sperated_by_comma = command[5:].split(' ')
        if len(tasks_sperated_by_comma) == 1:
            ids_to_done = tasks_sperated_by_comma[0].split(',')
            if all(i.isdigit() for i in ids_to_done):
                for id_to_done in ids_to_done:
                    index_to_done = int(id_to_done) - 1
                    if 0 <= index_to_done < len(task_list):
                        done_list.append(copy.copy(task_list[index_to_done]))
                        task_list[index_to_done]['status'] = not task_list[index_to_done]['status']
                        tsk.save_tasks(task_list, tsk.tasks_file_path)
    elif command.startswith("flag "):
        tasks_sperated_by_comma = command[5:].split(' ')
        if len(tasks_sperated_by_comma) == 1:
            ids_to_flag = tasks_sperated_by_comma[0].split(',')
            if all(i.isdigit() for i in ids_to_flag):
                for id_to_flag in ids_to_flag:
                    index_to_flag = int(id_to_flag) - 1
                    if 0 <= index_to_flag < len(task_list):
                        done_list.append(copy.copy(task_list[index_to_flag]))
                        task_list[index_to_flag]['flagged'] = not task_list[index_to_flag]['flagged']
                        tsk.save_tasks(task_list, tsk.tasks_file_path)
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
    elif command == "purge all":
        task_list = []
        tsk.save_tasks(task_list, tsk.tasks_file_path)
    elif command.startswith("sort "):
        category = command[5:]
        if category == "f":
            task_list = sort(task_list, "flagged")
            tsk.reassign_task_ids(task_list)
        elif category == 'd':
            task_list = sort(task_list, "status")
            tsk.reassign_task_ids(task_list)
    elif command == "group":
        pass
    elif command.startswith("color "):
        st.set_color_selected(command[6:])
    elif command == "help":
        stdscr.erase()
        pr.print_msg(stdscr, pr.help_msg)
        while stdscr.getch() != ord('q'):
            continue
    elif command.startswith("del"):
        # In order to apply post_deletion_update, need to first change 
        # current_id & current_row to the the one to be deleted
        del_task_id = command[4:]
        if del_task_id.isdigit():
            # only deletion of task in current view is allowed
            if start <= int(del_task_id) <= end:
                old_current_id = current_id
                # old_current_row = current_row
                current_id = int(del_task_id)
                current_row = current_id - start + 1
                old_description = task_list[old_current_id - 1]['description']
                del task_list[int(del_task_id) - 1]
                tsk.reassign_task_ids(task_list)
                _, _, start, end = scr.post_deletion_update(
                                                            current_id,
                                                            current_row, 
                                                            start, 
                                                            end,
                                                            len(task_list) + 1,
                                                            max_capacity
                                                            )
                # restore to previous current_id and current_row
                # These 2 remain unchaned unless the last task was deleted:
                new_id_of_prev_current_task = get_id_by_description(task_list, old_description)
                # if the prev current task was deleted: the selected task was deleted
                if new_id_of_prev_current_task == -1:
                    # if the first task was selected and deleted
                    if old_current_id == 1:
                        current_id = 1
                    else:
                        current_id = old_current_id - 1
                else:
                    current_id = new_id_of_prev_current_task
                current_row = current_id - start + 1
                tsk.save_tasks(task_list, tsk.tasks_file_path)
                                        
    elif command.startswith("edit"):
        task_id = command[5:]
        if task_id.isdigit() and int(task_id) <= len(task_list):
            max_capacity = stdscr.getmaxyx()[0] - 1    
            edit_id = int(task_id)
            pr.repaint(stdscr, len(done_list), len(task_list), task_list, edit_id, start, end)
            curses.echo()
            curses.curs_set(1)
            current_row = edit_id - start + 1
            if len(task_list) and edit_id >= start and edit_id <= end:
                current_id, current_row, start, end = ut.edit_and_save(
                    stdscr, 
                    task_list, 
                    edit_id,
                    current_row,
                    start,
                    end,
                    edit_id - start + 1,
                    len(task_list[edit_id - 1]['description']) + ut.indent,
                    max_capacity
                )
            curses.curs_set(0)
            curses.noecho()      
    elif command.startswith("st"):
        option = command[3:]
        if option == "on":
            st.set_strikethrough(True)
        elif option == "off":
            st.set_strikethrough(False)
        # Repaint the screen to show the change immediately
        pr.repaint(stdscr, len(done_list), len(task_list), task_list, current_id, start, end)
    

    return task_list, done_list, current_id, current_row, start, end

def get_id_by_description(task_list, description):
    # current solution: save the content of the prev task first
    # or just iterate through the whole list to match description
    # then restore back to the new id corresponding to that content
    
    # todo: python dict should support reverse retrieving
    for task in task_list:
        if task['description'] == description:
            return task['id']
    return -1

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


