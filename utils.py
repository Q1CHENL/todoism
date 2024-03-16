import copy
import curses
from datetime import datetime
from task import *
from print import *


indent = 6
description_length = 75
task_highlighting_color = curses.COLOR_BLUE

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
    save_tasks(purged_list, purged_file_path)
    return remained, []
    
def execute_command(stdscr, command, task_list, done_list, purged_list, current_id):
    global task_highlighting_color
    if command.startswith("add "):
        new_task = command[4:]
        if new_task:
            task_list.append({'description': new_task, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'status': False})
    elif command.startswith("done "):
        index_to_delete = int(command[7:]) - 1
        if 0 <= index_to_delete < len(task_list):
            done_list.append(copy.copy(task_list[index_to_delete]))
            task_list[index_to_delete]['status'] = not task_list[index_to_delete]['status']
    elif command == "purge":
        original_cnt = len(task_list)
        task_list, done_list = purge(task_list, purged_list)
        save_tasks(task_list, tasks_file_path)
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
        elif category == 'd':
            done_tasks = []
            not_done = []
            for t in task_list:
                if t['status'] == True:
                    done_tasks.append(t)
                else:
                    not_done.append(t)
            task_list = not_done + done_tasks
    elif command == "group":
        pass
    elif command.startswith("setcolor "):
        color = command[9:]
        if color == "red":
            task_highlighting_color = curses.COLOR_RED
        elif color == "blue":
            task_highlighting_color = curses.COLOR_BLUE
        elif color == "yellow":
            task_highlighting_color = curses.COLOR_YELLOW
        elif color == "green":
            task_highlighting_color = curses.COLOR_GREEN
    elif command == "help":
        print_help(stdscr)
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
        if ch == 10: # Enter to complete
            break
        elif ch == curses.KEY_LEFT:
            stdscr.move(y, indent if x <= indent else x - 1) # cursor remains still
        elif ch == curses.KEY_RIGHT:
            stdscr.move(y, x + 1 if x < indent + len(task['description']) else indent + len(task['description']))
        elif ch == curses.KEY_BACKSPACE or ch == 127: # delete
            if x <= 6:
                stdscr.move(y, indent) # cursor remains still
                continue
            # -1 because i am deleting the char before the cursor
            task['description'] = task['description'][:x - indent - 1] + task['description'][x - indent:]
            print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x - 1)
        elif 32 <= ch < 127: # printable char
            task['description'] = task['description'][:x - indent] + chr(ch) + task['description'][x - indent:]
            print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x + 1)        
        elif ch == 27 and mode == add_mode: # todo: too slow
            return ""
    return task['description']
    # todo sound
    # selected color