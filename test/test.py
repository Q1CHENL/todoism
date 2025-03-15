import os
import json
import uuid
import shutil
import todoism.preference as pref
import todoism.task as tsk

# Backup file paths for saving the actual data
backup_file_path = os.path.join(pref.config_dir, "tasks_backup.json")
backup_categories_path = os.path.join(pref.config_dir, "categories_backup.json")

# Flag file to mark that we're in test mode
test_mode_flag_path = os.path.join(pref.config_dir, "test_mode_active")

def generate_test_tasks():
    """Generate a fresh set of test tasks with proper UUIDs and category_id"""
    test_tasks = [
        {
            "id": 1,
            "uuid": str(uuid.uuid4()),
            "description": "Implement test mode",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": True,
            "category_id": 0
        },
        {
            "id": 2,
            "uuid": str(uuid.uuid4()),
            "description": "Sort by flagged or done",
            "date": tsk.formatted_datetime_now(),
            "status": True,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 3,
            "uuid": str(uuid.uuid4()),
            "description": "Auto update todoism",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 4,
            "uuid": str(uuid.uuid4()),
            "description": "Work category task example",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 1
        },
        {
            "id": 5,
            "uuid": str(uuid.uuid4()),
            "description": "Personal category task example",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": True,
            "category_id": 2
        },
        {
            "id": 6,
            "uuid": str(uuid.uuid4()),
            "description": "Very long task description for testing text wrapping and scrolling behavior in the todoism terminal user interface",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 0
        },
        # Additional tasks
        {
            "id": 7,
            "uuid": str(uuid.uuid4()),
            "description": "Call dentist for appointment",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": True,
            "category_id": 3  # Health
        },
        {
            "id": 8,
            "uuid": str(uuid.uuid4()),
            "description": "Buy groceries for the week",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 4  # Shopping
        },
        {
            "id": 9,
            "uuid": str(uuid.uuid4()),
            "description": "Finish quarterly report",
            "date": tsk.formatted_datetime_now(),
            "status": True,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 10,
            "uuid": str(uuid.uuid4()),
            "description": "Research new programming language",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 11,
            "uuid": str(uuid.uuid4()),
            "description": "Plan weekend trip",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": True,
            "category_id": 6  # Travel
        },
        {
            "id": 12,
            "uuid": str(uuid.uuid4()),
            "description": "Fix bathroom sink",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 7  # Home
        },
        {
            "id": 13,
            "uuid": str(uuid.uuid4()),
            "description": "Schedule team meeting",
            "date": tsk.formatted_datetime_now(),
            "status": True,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 14,
            "uuid": str(uuid.uuid4()),
            "description": "Create weekly workout plan",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 15,
            "uuid": str(uuid.uuid4()),
            "description": "Read new book on productivity",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 16,
            "uuid": str(uuid.uuid4()),
            "description": "Update resume",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": True,
            "category_id": 9  # Career
        },
        {
            "id": 17,
            "uuid": str(uuid.uuid4()),
            "description": "Pay monthly bills",
            "date": tsk.formatted_datetime_now(),
            "status": True,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 18,
            "uuid": str(uuid.uuid4()),
            "description": "Organize digital files",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 19,
            "uuid": str(uuid.uuid4()),
            "description": "Order birthday gift for mom",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": True,
            "category_id": 4  # Shopping
        },
        {
            "id": 20,
            "uuid": str(uuid.uuid4()),
            "description": "Sign up for new fitness class",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 21,
            "uuid": str(uuid.uuid4()),
            "description": "Finish home improvement project",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 7  # Home
        },
        {
            "id": 22,
            "uuid": str(uuid.uuid4()),
            "description": "Research vacation destinations",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 6  # Travel
        },
        {
            "id": 23,
            "uuid": str(uuid.uuid4()),
            "description": "Attend dental checkup",
            "date": tsk.formatted_datetime_now(),
            "status": True,
            "flagged": False,
            "category_id": 3  # Health
        },
        {
            "id": 24,
            "uuid": str(uuid.uuid4()),
            "description": "Complete online course",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": True,
            "category_id": 5  # Learning
        },
        {
            "id": 25,
            "uuid": str(uuid.uuid4()),
            "description": "Review annual budget",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 26,
            "uuid": str(uuid.uuid4()),
            "description": "Prepare presentation for client meeting",
            "date": tsk.formatted_datetime_now(),
            "status": False, 
            "flagged": True,
            "category_id": 1  # Work
        },
        {
            "id": 27,
            "uuid": str(uuid.uuid4()),
            "description": "Another task with very long description to test horizontal scrolling and ensure proper text display in the terminal interface",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 9  # Career
        },
        {
            "id": 28,
            "uuid": str(uuid.uuid4()),
            "description": "Buy new workout equipment",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 29,
            "uuid": str(uuid.uuid4()),
            "description": "Schedule annual doctor checkup",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 3  # Health
        },
        {
            "id": 30,
            "uuid": str(uuid.uuid4()),
            "description": "Clean garage",
            "date": tsk.formatted_datetime_now(),
            "status": False,
            "flagged": False,
            "category_id": 7  # Home
        }
    ]
    return test_tasks

def generate_test_categories():
    """Generate test categories"""
    test_categories = [
        {
            "id": 0,
            "name": "All Tasks"
        },
        {
            "id": 1,
            "name": "Work"
        },
        {
            "id": 2,
            "name": "Personal"
        },
        {
            "id": 3,
            "name": "Health"
        },
        {
            "id": 4,
            "name": "Shopping"
        },
        {
            "id": 5,
            "name": "Learning"
        },
        {
            "id": 6,
            "name": "Travel"
        },
        {
            "id": 7,
            "name": "Home"
        },
        {
            "id": 8,
            "name": "Fitness"
        },
        {
            "id": 9,
            "name": "Career"
        }
    ]
    return test_categories

def is_test_mode_active():
    """Check if test mode is currently active"""
    return os.path.exists(test_mode_flag_path)

def backup_data():
    """Backup current tasks and categories before loading test data"""
    try:
        import todoism.category as cat
        success = True
        
        # Backup tasks if they exist
        if os.path.exists(pref.tasks_file_path):
            shutil.copy2(pref.tasks_file_path, backup_file_path)
        else:
            success = False
            
        # Backup categories if they exist
        if os.path.exists(pref.categories_file_path):
            shutil.copy2(pref.categories_file_path, backup_categories_path)
        else:
            success = False
            
        # Create a flag file to indicate test mode is active
        with open(test_mode_flag_path, 'w') as f:
            f.write('1')
            
        return success
    except Exception as e:
        print(f"Error backing up data: {e}")
        return False

def restore_data():
    """Restore tasks and categories from backup"""
    try:
        import todoism.category as cat
        success = True
        
        # Restore tasks if backup exists
        if os.path.exists(backup_file_path):
            shutil.copy2(backup_file_path, pref.tasks_file_path)
            # Clean up backup file
            os.remove(backup_file_path)
        else:
            success = False
            
        # Restore categories if backup exists
        if os.path.exists(backup_categories_path):
            shutil.copy2(backup_categories_path, pref.categories_file_path)
            # Clean up backup file
            os.remove(backup_categories_path)
        else:
            success = False
            
        # Remove test mode flag
        if os.path.exists(test_mode_flag_path):
            os.remove(test_mode_flag_path)
            
        # Clean up test file if it exists
        if os.path.exists(pref.test_file_path):
            os.remove(pref.test_file_path)
            
        return success
    except Exception as e:
        print(f"Error restoring data: {e}")
        return False

def load_test_mode():
    """Load test tasks and categories"""
    # Backup current data
    backup_data()
    
    # Generate test data
    test_tasks = generate_test_tasks()
    test_categories = generate_test_categories()
    
    import todoism.category as cat
    
    # Clear any existing categories first to ensure isolation
    # Use the exact replacement approach - write only our test categories
    with open(pref.categories_file_path, 'w') as file:
        json.dump(test_categories, file, indent=4)
    
    # Save tasks in both locations
    with open(pref.test_file_path, 'w') as file:
        json.dump(test_tasks, file, indent=4)
    
    with open(pref.tasks_file_path, 'w') as file:
        json.dump(test_tasks, file, indent=4)
    
    return True

def exit_test_mode():
    """Exit test mode by restoring original data"""
    return restore_data()

if __name__ == "__main__":
    # When run directly, generate and save test data
    load_test_mode()
    print("Test mode enabled. Test tasks and categories created.")

