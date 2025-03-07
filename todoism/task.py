import os
import json
import todoism.utils as ut
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

def create_new_task(task_id, task_description="", flagged=False):
    return {
        'id': task_id,
        'description': task_description,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'status': False,
        'flagged': flagged
    }

def save_tasks(task_list, path):
    with open(path, 'w') as file:
        json.dump(task_list, file, indent=4)

def add_new_task(task_list, task_id, task_description, flagged=False):
    """create, append and save a new task with id: task_id and description: task_description to task_list"""
    new_task = create_new_task(task_id, task_description, flagged)
    task_list.append(new_task)
    save_tasks(task_list, tasks_file_path)
    return task_list

def add_new_task_cli(task_description, flagged=False):
    task_list = load_tasks()
    task_id = len(task_list) + 1
    _ = add_new_task(task_list, task_id, task_description, flagged)[-1]
    return task_id

def remove_task_cli(task_id):
    task_list = load_tasks()
    if task_id <= len(task_list):
        del task_list[task_id - 1]
        tsk.reassign_task_ids(task_list)
        save_tasks(task_list, tasks_file_path)   
        return True

def create_new_task(task_id, task_description="", flagged=False, category_id=0):
    """Create a new task with optional category assignment"""
    return {
        'id': task_id,
        'description': task_description,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'status': False,
        'flagged': flagged,
        'category_id': category_id  # Default to 'All' category (id=0)
    }

def add_new_task(task_list, task_id, task_description, flagged=False, category_id=0):
    """Create, append and save a new task with category support"""
    new_task = create_new_task(task_id, task_description, flagged, category_id)
    task_list.append(new_task)
    save_tasks(task_list, tasks_file_path)
    return task_list

def get_tasks_by_category(task_list, category_id):
    """Filter tasks by category"""
    if category_id == 0:  # 'All' category
        return task_list
    
    result = []
    for task in task_list:
        # Handle tasks from before categories were implemented
        task_category = task.get('category_id', 0)
        if task_category == category_id:
            result.append(task)
    return result

def update_existing_tasks():
    """Update existing tasks to include category_id field if missing"""
    task_list = load_tasks()
    modified = False
    
    for task in task_list:
        if 'category_id' not in task:
            task['category_id'] = 0  # Default to "All" category
            modified = True
    
    if modified:
        save_tasks(task_list, tasks_file_path)
    
    return task_list

def reassign_task_ids(task_list):
    """Reassign ids to every task in the list"""
    for i, t in enumerate(task_list):
        t['id'] = i + 1