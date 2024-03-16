import os
import json
import copy
import curses
from datetime import datetime


add_mode  = 0
edit_mode = 1

indent = 6
description_length = 75

home_dir = os.path.expanduser("~")
config_dir = os.path.join(home_dir, ".todoism")
os.makedirs(config_dir, exist_ok=True)
tasks_file_path = os.path.join(config_dir, "tasks.json")
purged_file_path = os.path.join(config_dir, "purged.json")
test_file_path = os.path.join(config_dir, "test.json")

help_msg =  '''
                            ┌─────────────────────────────────────────────┐
                            │              a: create new task             │
                            │              q: quit todoism                │
                            │              e: edit task                   │
                            │                                             │
                            │              :<command> [args]              │
                            │              commands:                      │
                            │              help, sort [f] [d], purge      │
                            ├─────────────────────────────────────────────┤
                            └─────────────────────────────────────────────┘
            '''

def print_help(stdscr):
    height, width = stdscr.getmaxyx()
    stdscr.addstr((height // 2) - 4, (width // 2) + 50, help_msg)
    stdscr.refresh()

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

def reid(tasks):
    for i, t in enumerate(tasks):
        t['id'] = i + 1
    
# The core function to print task
def print_task(stdscr, task, y):
    maxy = stdscr.getmaxyx()[0] 
    # handle task overflow
    if y < maxy:
        stdscr.addstr(y, 0, f"{'✅' if task['status'] else '  '} {task['id']}. {task['description'] + (75 - len(task['description'])) * ' ' + task['date']} {'🚩' if task['flagged'] else ''}" )

def print_task_highlighted(stdscr, task, y):
    stdscr.attron(curses.color_pair(1))
    print_task(stdscr, task, y)
    stdscr.attroff(curses.color_pair(1))        

def print_task_mode(stdscr, task, y, mode):
    if mode == edit_mode:
        print_task_highlighted(stdscr, task, y)
    else:
        print_task(stdscr, task, y)  
        
def print_tasks(stdscr, tasks, current_id, start, end):
    if start > 0:
        for i, task in enumerate(tasks[start - 1:end + 1]):
            if i + start == current_id: # handle task overflow: +start
                print_task_highlighted(stdscr, task, i + 1) # +1 due to status bar
            else:
                print_task(stdscr, task, i + 1)

def print_status_bar(stdscr, done_cnt, task_cnt):
    percentage_num = int((done_cnt / task_cnt) * 100) if task_cnt > 0 else 0
    status_bar = {
        'tasks': f'{' '*35}Progress: {done_cnt}/{task_cnt} {percentage_num if task_cnt > 0 else 0}%',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M") 
    }
    color_pair = 0
    if percentage_num >= 67:
        color_pair = 2
    elif percentage_num >= 33:
        color_pair = 3
    else:
        color_pair = 4
    stdscr.attron(curses.color_pair(color_pair))    
    stdscr.addstr(0, 0, f"{status_bar['tasks']}")
    stdscr.attroff(curses.color_pair(color_pair))
    stdscr.addstr(f" | {status_bar['date']}")
    stdscr.refresh()

def done_count(tasks):
    count = 0
    for t in tasks:
        if t['status'] is True:
            count = count + 1
    return count        
            
def load_tasks(arg=''):
    try:
        with open(test_file_path if arg == '-t' else tasks_file_path, 'r') as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []
    return tasks

def create_new_task(task_id, task_description=""):
    return {
        'id': task_id,
        'description': task_description,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'status': False,
        'flagged': False
    }

def save_tasks(tasks, path):
    with open(path, 'w') as file:
        json.dump(tasks, file, indent=4)

def add_new_task(tasks, task_id, task_description):
    new_task = create_new_task(task_id, task_description)
    tasks.append(new_task)
    save_tasks(tasks, tasks_file_path)
    return tasks
    
def execute_command(stdscr, command, task_list, done_list, purged_list, current_id):
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
    elif command == "help":
        print_help(stdscr)
        key = stdscr.getch()
        if key == ord('q'):
            stdscr.clear()
    return task_list, done_list, current_id

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