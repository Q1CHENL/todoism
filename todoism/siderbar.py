import json
import todoism.path as path

siderbar_width = 25

def create_new_category(category_id, name):
    return {
        'category_id': category_id,
        'category': name,
        'task_list': []
    }

def add_new_category(category_list, category_id, category_name):
    """create, append and save a new task with id: task_id and description: task_description to task_list"""
    new_task = create_new_category(category_id, category_name)
    category_list.append(new_task)
    save_categories(category_list, path.tasks_file_path)
    return category_list

def save_categories(category_list, path):
    with open(path, 'w') as file:
        json.dump(category_list, file, indent=4)
