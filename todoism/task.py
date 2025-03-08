import os
import json
import todoism.edit as ed
from datetime import datetime
import uuid

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

def create_new_task(task_id, task_description="", flagged=False, category_id=0):
    """Create a new task with UUID and optional category assignment"""
    return {
        'uuid': str(uuid.uuid4()),
        'id': task_id,
        'description': task_description,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'status': False,
        'flagged': flagged,
        'category_id': category_id
    }

def save_tasks(task_list, path):
    with open(path, 'w') as file:
        json.dump(task_list, file, indent=4)

def add_new_task_cli(task_description, flagged=False):
    task_list = load_tasks()
    task_id = len(task_list) + 1
    new_task = create_new_task(task_id, task_description, flagged)
    task_list.append(new_task)
    save_tasks(task_list, tasks_file_path)
    return task_id

def remove_task_cli(task_id):
    """Remove a task by its display ID from the command line"""
    task_list = load_tasks()
    if task_id <= len(task_list):
        task_uuid = task_list[task_id - 1].get('uuid')
        if task_uuid:
            task_list = delete_task_by_uuid(task_list, task_uuid)
        else:
            # Fallback for legacy tasks
            del task_list[task_id - 1]
            reassign_task_ids(task_list)
            save_tasks(task_list, tasks_file_path)
        return True
    return False

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
        task_category = task.get('category_id', 0)
        if task_category == category_id:
            result.append(task)
    return result

def update_existing_tasks():
    """Update existing tasks to include category_id and uuid fields if missing"""
    task_list = load_tasks()
    modified = False
    
    for task in task_list:
        if 'category_id' not in task:
            task['category_id'] = 0
            modified = True
        
        if 'uuid' not in task:
            task['uuid'] = str(uuid.uuid4())
            modified = True
    
    if modified:
        save_tasks(task_list, tasks_file_path)
    
    return task_list

def reassign_task_ids(task_list):
    """Reassign ids to every task in the list"""
    for i, t in enumerate(task_list):
        t['id'] = i + 1

def delete_task_by_uuid(task_list, task_uuid):
    """Delete task by UUID and return updated list"""
    task_list = [task for task in task_list if task.get('uuid') != task_uuid]
    reassign_task_ids(task_list)
    save_tasks(task_list, tasks_file_path)
    return task_list

def done_task_by_uuid(task_list, task_uuid):
    """Mark task as done by UUID and return updated list"""
    for task in task_list:
        if task.get('uuid') == task_uuid:
            task['status'] = True
            save_tasks(task_list, tasks_file_path)
            return task_list
    return task_list

def flag_task_by_uuid(task_list, task_uuid):
    """Flag task by UUID and return updated list"""
    for task in task_list:
        if task.get('uuid') == task_uuid:
            task['flagged'] = not task.get('flagged', False)
            save_tasks(task_list, tasks_file_path)
            return task_list
    return task_list