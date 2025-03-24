import json

import todoism.preference as pref

MAX_CATEGORY_NAME_LENGTH = 12
MAX_CATEGORY_COUNT = 128
SIDEBAR_WIDTH = 16
NAME_INDENT = 2

def load_categories():
    """Load categories from file"""
    try:
        with open(pref.get_categories_path(), 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If categories file doesn't exist, create it with default "All Tasks"
        default_categories = [{"id": 0, "name": "All Tasks"}]
        save_categories(default_categories)
        return default_categories

def save_categories(category_list):
    """Save categories to the categories.json file"""
    with open(pref.get_categories_path(), 'w') as file:
        json.dump(category_list, file, indent=4)

def create_category(name, color="blue"):
    """Create a new category object"""
    categories = load_categories()
    new_id = max([cat["id"] for cat in categories], default=-1) + 1

    if new_id > MAX_CATEGORY_COUNT:
        return None
        
    new_category = {
        "id": new_id,
        "name": name
    }
    
    return new_category

def add_category(name, color="blue"):
    """Create and save a new category"""
    new_category = create_category(name, color)
    if new_category:
        categories = load_categories()
        categories.append(new_category)
        save_categories(categories)
        return new_category
    return None

def delete_category(category_id):
    """Delete a category by ID"""
    categories = load_categories()
    # Can't delete the "All" category (id=0)
    if category_id == 0:
        return False
        
    for i, category in enumerate(categories):
        if category["id"] == category_id:
            del categories[i]
            save_categories(categories)
            return True
    return False

def update_category_name(category_id, new_name):
    """Update a category's name"""
    categories = load_categories()
    for category in categories:
        if category["id"] == category_id:
            category["name"] = new_name
            save_categories(categories)
            return True
    return False

def get_category_by_id(category_id):
    """Get a category by its ID"""
    categories = load_categories()
    for category in categories:
        if category["id"] == category_id:
            return category
    return None

def reassign_category_ids():
    """Reassign IDs to categories in sequence, preserving the 'All' category as ID 0"""
    categories = load_categories()
    
    # Separate "All" category from the rest
    all_category = next((cat for cat in categories if cat["id"] == 0), None)
    other_categories = [cat for cat in categories if cat["id"] != 0]
    
    # Reassign IDs to other categories
    for i, category in enumerate(other_categories):
        category["id"] = i + 1
    
    # Reconstruct the list with "All" at the beginning
    result = [all_category] if all_category else []
    result.extend(other_categories)
    
    save_categories(result)
    return result