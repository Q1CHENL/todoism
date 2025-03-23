import json
import uuid
from datetime import datetime
import todoism.preference as pref

MAX_TASK_DESCRIPTION_LENGTH = 256
TASK_INDENT_IN_TASK_PANEL = 7 # ID (2) + space (1) + flag (1) + space (1) + done (1) + space (1)
MAX_TASK_COUNT = 1024

def done_count(task_list):
    count = 0
    for t in task_list:
        if t["status"] is True:
            count = count + 1
    return count        

def get_tasks_file_path():
    """Get the correct tasks file path based on whether dev mode is active"""
    try:
        import test.test as test
        if test.is_dev_mode_active():
            return pref.test_tasks_file_path
        return pref.tasks_file_path
    except ImportError:
        return pref.tasks_file_path

def load_tasks():
    """Load tasks from file"""
    try:
        with open(get_tasks_file_path(), 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_purged_tasks():
    try:
        with open(pref.purged_file_path, 'r') as f:
            purged_tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        purged_tasks = []
    return purged_tasks

def create_new_task(task_id, task_description="", flagged=False, category_id=0, due=""):
    """Create a new task with UUID and optional category assignment"""
    return {
        "uuid": str(uuid.uuid4()),
        "id": task_id,
        "description": task_description,
        "due": due,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": False,
        "flagged": flagged,
        "category_id": category_id
    }

def save_tasks(task_list, custom_path=None):
    """Save tasks to file"""
    if custom_path:
        file_path = custom_path
    else:
        file_path = get_tasks_file_path()
    
    with open(file_path, 'w') as file:
        json.dump(task_list, file, indent=4)

def add_new_task_cli(task_description, flagged=False):
    task_list = load_tasks()
    new_task_id = len(task_list) + 1
    new_task = create_new_task(new_task_id, task_description, flagged)
    task_list.append(new_task)
    save_tasks(task_list)
    return new_task_id

def delete_task_cli(task_id):
    """Remove a task by its display ID from the command line"""
    task_list = load_tasks()
    reassign_task_ids(task_list)
    if task_id <= len(task_list):
        task_uuid = task_list[task_id - 1].get("uuid")
        if task_uuid:
            task_list = delete_task_by_uuid(task_list, task_uuid)
        return True
    return False

def add_new_task(task_list, task_id, task_description, flagged=False, category_id=0, due=""):
    """Create, append and save a new task with category support"""
    new_task = create_new_task(task_id, task_description, flagged, category_id, due)
    task_list.append(new_task)
    save_tasks(task_list)
    return task_list

def get_tasks_by_category_id(task_list, category_id):
    """Filter tasks by category"""
    if category_id == 0:  # All Tasks category
        return task_list
    
    result = []
    for task in task_list:
        task_category = task.get("category_id", 0)
        if task_category == category_id:
            result.append(task)
    return result

def update_existing_tasks():
    """Update existing tasks to include category_id and uuid fields if missing"""
    task_list = load_tasks()
    modified = False
    
    for task in task_list:
        if "category_id" not in task:
            task["category_id"] = 0
            modified = True
        
        if "uuid" not in task:
            task["uuid"] = str(uuid.uuid4())
            modified = True
        
        if "due" not in task:
            task["due"] = ""
            modified = True
        
        if "created" not in task:
            task["created"] = ""
            modified = True
    
    if modified:
        save_tasks(task_list)
    
    return task_list

def reassign_task_ids(task_list):
    """Reassign ids to every task in the list"""
    for i, t in enumerate(task_list):
        t["id"] = i + 1

def delete_task_by_uuid(task_list, task_uuid):
    """Delete task by UUID and return updated list"""
    task_list = [task for task in task_list if task.get("uuid") != task_uuid]
    reassign_task_ids(task_list)
    save_tasks(task_list)
    return task_list

def done_task_by_uuid(task_list, task_uuid):
    """Mark task as done by UUID and return updated list"""
    for task in task_list:
        if task.get("uuid") == task_uuid:
            task["status"] = True
            save_tasks(task_list)
            return task_list
    return task_list

def flag_task_by_uuid(task_list, task_uuid):
    """Flag task by UUID and return updated list"""
    for task in task_list:
        if task.get("uuid") == task_uuid:
            task["flagged"] = not task.get("flagged", False)
            save_tasks(task_list)
            return task_list
    return task_list

def sort(task_list, key) -> list:
    marked = []
    not_marked = []
    for t in task_list:
        if t[key] is True:
            marked.append(t)
        else:
            not_marked.append(t)
    return marked + not_marked
