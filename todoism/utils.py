import copy
import json
import curses
from datetime import datetime
import todoism.task as tsk
import todoism.print as tprint


indent = 7
description_length = 75
task_highlighting_color = curses.COLOR_BLUE

color_set = {
    "blue": curses.COLOR_BLUE,
    "red": curses.COLOR_RED,
    "yellow": curses.COLOR_YELLOW,
    "green": curses.COLOR_GREEN
}


def get_arg(argv):
    if len(argv) > 1:
        return argv[1]
    else:
        return ""


def reid(tasks):
    for i, t in enumerate(tasks):
        t['id'] = i + 1


def purge(tasks, purged_list):
    """
    purge completed tasks
    """
    remained = []
    for t in tasks:
        if t['status'] is False:
            remained.append(t)
        else:
            purged_list.append(t)
    reid(remained)
    tsk.save_tasks(purged_list, tsk.purged_file_path)
    return remained, []


def execute_command(stdscr, command, task_list, done_list, purged_list, current_id):
    global task_highlighting_color
    if command.startswith("add "):
        new_task = command[4:]
        if new_task:
            task_list.append({'description': new_task, 'date': datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"), 'status': False})
    elif command.startswith("done "):
        index_to_delete = int(command[7:]) - 1
        if 0 <= index_to_delete < len(task_list):
            done_list.append(copy.copy(task_list[index_to_delete]))
            task_list[index_to_delete]['status'] = not task_list[index_to_delete]['status']
    elif command == "purge":
        original_cnt = len(task_list)
        task_list, done_list = purge(task_list, purged_list)
        tsk.save_tasks(task_list, tsk.tasks_file_path)
        # change current id if some tasks were purged
        if len(task_list) < original_cnt:
            current_id = 1
    elif command.startswith("sort "):
        category = command[5:]
        if category == "f":
            flagged_tasks = []
            not_flagged = []
            for t in task_list:
                if t['flagged'] is True:
                    flagged_tasks.append(t)
                else:
                    not_flagged.append(t)
            task_list = flagged_tasks + not_flagged
            reid(task_list)
        elif category == 'd':
            done_tasks = []
            not_done = []
            for t in task_list:
                if t['status'] == True:
                    done_tasks.append(t)
                else:
                    not_done.append(t)
            task_list = not_done + done_tasks
            reid(task_list)
    elif command == "group":
        pass
    elif command.startswith("setcolor "):
        set_color_selected(command[9:])
    elif command == "help":
        tprint.print_help(stdscr)
        key = stdscr.getch()
        if key == ord('q'):
            stdscr.clear()
    # have to return task_highlighting_color, otherwise not accessible in main --> weird
    return task_list, done_list, current_id, task_highlighting_color


def edit(stdscr, task, mode):
    """
    A editing wrapper implemented using getch(). It delivers 
    more comprehensive functionalities than getstr() does.
    """
    while True:
        y, x = stdscr.getyx()
        ch = stdscr.getch()
        if ch == 10:  # Enter to complete
            break
        elif ch == curses.KEY_LEFT:
            # cursor remains still
            stdscr.move(y, indent if x <= indent else x - 1)
        elif ch == curses.KEY_RIGHT:
            stdscr.move(y, x + 1 if x < indent +
                        len(task['description']) else indent + len(task['description']))
        elif ch == curses.KEY_BACKSPACE or ch == 127:  # delete
            if x <= 7:
                stdscr.move(y, indent)  # cursor remains still
                continue
            # -1 because i am deleting the char before the cursor
            task['description'] = task['description'][:x -
                                                      indent - 1] + task['description'][x - indent:]
            tprint.print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x - 1)
        elif 32 <= ch < 127:  # printable char
            task['description'] = task['description'][:x - indent] + \
                chr(ch) + task['description'][x - indent:]
            tprint.print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x + 1)
        elif ch == 27 and mode == tprint.add_mode:  # todo: too slow
            return ""
    return task['description']


def set_color_selected(color: str):
    # invalid color
    if color not in color_set:
        return
    try:
        with open(tsk.settings_path, "r+") as settings_file:
            settings = json.load(settings_file)
            settings['task_highlighting_color'] = color
            settings_file.seek(0)  # move pointer back to beginning
            json.dump(settings, settings_file, indent=4)
            settings_file.truncate()
    except FileNotFoundError:
        setup_default_settings()


def get_color_selected():
    try:
        with open(tsk.settings_path, "r") as settings_file:
            settings = json.load(settings_file)
            color = settings['task_highlighting_color']
            return color_set[color]
    except FileNotFoundError:
        setup_default_settings()
        return curses.COLOR_BLUE


def setup_default_settings():
    """
    setup default settings if no settings.json were found
    """
    default_settings = {
        "date_format": "Y-M-D",
        "scroll": True,
        "autosort_f": False,
        "autosort_d": False,
        "task_highlighting_color": "blue"
    }
    with open(tsk.settings_path, "w") as file:
        json.dump(default_settings, file, indent=4)
    return default_settings

def is_view_fully_packed(start, end, max_count):
    """indicates whether the current view is completely filled with tasks"""
    return end - start + 1 >= max_count
    