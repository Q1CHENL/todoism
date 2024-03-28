import curses
import copy

import todoism.task as tsk
import todoism.utils as ut
import todoism.print as pr
import todoism.settings as st


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
    ut.reid(remained)
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


def execute_command(stdscr, command, task_list, done_list, purged_list, current_id, start, end, current_row):
    if command.startswith("done "):
        if command[5:].isdigit():
            index_to_done = int(command[5:]) - 1
            if 0 <= index_to_done < len(task_list):
                done_list.append(copy.copy(task_list[index_to_done]))
                task_list[index_to_done]['status'] = not task_list[index_to_done]['status']
    elif command == "purge":
        original_cnt = len(task_list)
        task_list, done_list = purge(task_list, purged_list)
        tsk.save_tasks(task_list, tsk.tasks_file_path)
        # change current id to 1 if some tasks were purged
        if len(task_list) < original_cnt:
            current_id = 1
    elif command.startswith("sort "):
        category = command[5:]
        if category == "f":
            task_list = sort(task_list, "flagged")
            ut.reid(task_list)
        elif category == 'd':
            task_list = sort(task_list, "status")
            ut.reid(task_list)
    elif command == "group":
        pass
    elif command.startswith("setcolor "):
        st.set_color_selected(command[9:])
    elif command == "help":
        pr.print_msg(stdscr, pr.help_msg)
        key = stdscr.getch()
        if key == ord('q'):
            stdscr.clear()
    elif command.startswith("del"):
        task_id = command[4:]
        if task_id.isdigit():
            num = len(task_list)
            if int(task_id) <= num:
                del task_list[int(task_id) - 1]
                ut.reid(task_list)
                if current_id == num:
                    current_id = current_id - 1
    elif command.startswith("edit"):
        task_id = command[5:]
        if task_id.isdigit() and int(task_id) <= len(task_list):
            window_height = stdscr.getmaxyx()[0]    
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
                                                            window_height
                                                            )
            curses.curs_set(0)
            curses.noecho()      

    return task_list, done_list, current_id, current_row, start, end

