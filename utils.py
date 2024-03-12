import curses
import json
import os
from datetime import datetime
import copy

description_length = 75
home_dir = os.path.expanduser("~")
config_dir = os.path.join(home_dir, ".todoism")
os.makedirs(config_dir, exist_ok=True)
tasks_file_path = os.path.join(config_dir, "tasks.json")

def purge(tasks, done_list):
    """
    purge completed tasks
    """
    remained = []
    for t in tasks:
        if t['status'] is False:
            remained.append(t)
        else:
            done_list.append(t)
    return remained, done_list
    
def print_task(stdscr, task, y):
    stdscr.addstr(y, 0, f"{'✅' if task['status'] else '  '} {y + 1}. {task['description'] + (75-len(task['description'])) * ' ' + task['date']} {'🚩' if task['flagged'] else ''}" )

def print_task_highlighted(stdscr, task, y):
    stdscr.attron(curses.color_pair(1))
    print_task(stdscr, task, y)
    stdscr.attroff(curses.color_pair(1))        

def load_tasks():
    try:
        with open(tasks_file_path, 'r') as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []
    return tasks

def create_new_task(task_description):
    return {
        'description': task_description,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'status': False,
        'flagged': False
    }

def add_new_task(task_description):
    new_task = create_new_task(task_description)
    tasks = load_tasks()
    tasks.append(new_task)
    # save the newly added task
    with open(tasks_file_path, 'w') as file:
        json.dump(tasks, file, indent=2)
    return tasks

def save_tasks(tasks):
    with open(tasks_file_path, 'w') as file:
        json.dump(tasks, file, indent=2)
    

def execute_command(command, todo_list, done_list, current_row, show_hidden):
    if command.startswith("add "):
        new_task = command[4:]
        if new_task:
            todo_list.append({'description': new_task, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'status': False})
    elif command.startswith("done "):
        index_to_delete = int(command[7:]) - 1
        if 0 <= index_to_delete < len(todo_list):
            done_list.append(copy.copy(todo_list[index_to_delete]))
            todo_list[index_to_delete]['status'] = not todo_list[index_to_delete]['status']
    elif command == "toggle_hidden":
        show_hidden = not show_hidden
    elif command == "purge":
        todo_list, done_list = purge(todo_list, done_list)
        save_tasks(todo_list)
        current_row = 0
    elif command == "sort":
        pass
    elif command == "group":
        pass
            
    return todo_list, done_list, current_row, show_hidden
