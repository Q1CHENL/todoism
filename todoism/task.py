import os
import json
from datetime import datetime


home_dir = os.path.expanduser("~")
config_dir = os.path.join(home_dir, ".todoism")
os.makedirs(config_dir, exist_ok=True)
tasks_file_path = os.path.join(config_dir, "tasks.json")
purged_file_path = os.path.join(config_dir, "purged.json")
test_file_path = os.path.join(config_dir, "test.json")
settings_path = os.path.join(config_dir, "settings.json")

def done_count(task_list):
    count = 0
    for t in task_list:
        if t['status'] is True:
            count = count + 1
    return count        
            
def load_tasks(arg=''):
    try:
        with open(test_file_path if arg == '-t' else tasks_file_path, 'r') as file:
            task_list = json.load(file)
    except FileNotFoundError:
        task_list = []
    return task_list

def create_new_task(task_id, task_description=""):
    return {
        'id': task_id,
        'description': task_description,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'status': False,
        'flagged': False
    }

def save_tasks(task_list, path):
    with open(path, 'w') as file:
        json.dump(task_list, file, indent=4)

def add_new_task(task_list, task_id, task_description):
    """create, append and save a new task with id: task_id and description: task_description to task_list"""
    new_task = create_new_task(task_id, task_description)
    task_list.append(new_task)
    save_tasks(task_list, tasks_file_path)
    return task_list

    