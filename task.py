import os
import json
from datetime import datetime


home_dir = os.path.expanduser("~")
config_dir = os.path.join(home_dir, ".todoism")
os.makedirs(config_dir, exist_ok=True)
tasks_file_path = os.path.join(config_dir, "tasks.json")
purged_file_path = os.path.join(config_dir, "purged.json")
test_file_path = os.path.join(config_dir, "test.json")

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
    