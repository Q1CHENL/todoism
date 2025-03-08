import json
import uuid
import os
import shutil
from datetime import datetime
import todoism.task as tsk

# Backup file paths for saving the actual data
backup_file_path = os.path.join(tsk.config_dir, "tasks_backup.json")
backup_categories_path = os.path.join(tsk.config_dir, "categories_backup.json")

# Flag file to mark that we're in test mode
test_mode_flag_path = os.path.join(tsk.config_dir, "test_mode_active")

def generate_test_tasks():
    """Generate a fresh set of test tasks with proper UUIDs and category_id"""
    test_tasks = [
        {
            "id": 1,
            "uuid": str(uuid.uuid4()),
            "description": "Implement test mode",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": False,
            "flagged": True,
            "category_id": 0
        },
        {
            "id": 2,
            "uuid": str(uuid.uuid4()),
            "description": "Add autosort command",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": True,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 3,
            "uuid": str(uuid.uuid4()),
            "description": "Auto update todoism",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 4,
            "uuid": str(uuid.uuid4()),
            "description": "Work category task example",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": False,
            "flagged": False,
            "category_id": 1
        },
        {
            "id": 5,
            "uuid": str(uuid.uuid4()),
            "description": "Personal category task example",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": False,
            "flagged": True,
            "category_id": 2
        },
        {
            "id": 6,
            "uuid": str(uuid.uuid4()),
            "description": "Very long task description for testing text wrapping and scrolling behavior in the todoism terminal user interface",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": False,
            "flagged": False,
            "category_id": 0
        }
    ]
    return test_tasks

def generate_test_categories():
    """Generate test categories"""
    test_categories = [
        {
            "id": 0,
            "name": "All Tasks",
            "color": "blue",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        },
        {
            "id": 1,
            "name": "Work",
            "color": "red",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        },
        {
            "id": 2,
            "name": "Personal",
            "color": "green",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
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
        if os.path.exists(tsk.tasks_file_path):
            shutil.copy2(tsk.tasks_file_path, backup_file_path)
        else:
            success = False
            
        # Backup categories if they exist
        if os.path.exists(cat.categories_file_path):
            shutil.copy2(cat.categories_file_path, backup_categories_path)
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
            shutil.copy2(backup_file_path, tsk.tasks_file_path)
            # Clean up backup file
            os.remove(backup_file_path)
        else:
            success = False
            
        # Restore categories if backup exists
        if os.path.exists(backup_categories_path):
            shutil.copy2(backup_categories_path, cat.categories_file_path)
            # Clean up backup file
            os.remove(backup_categories_path)
        else:
            success = False
            
        # Remove test mode flag
        if os.path.exists(test_mode_flag_path):
            os.remove(test_mode_flag_path)
            
        # Clean up test file if it exists
        if os.path.exists(tsk.test_file_path):
            os.remove(tsk.test_file_path)
            
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
    with open(cat.categories_file_path, 'w') as file:
        json.dump(test_categories, file, indent=4)
    
    # Save tasks in both locations
    with open(tsk.test_file_path, 'w') as file:
        json.dump(test_tasks, file, indent=4)
    
    with open(tsk.tasks_file_path, 'w') as file:
        json.dump(test_tasks, file, indent=4)
    
    return True

def exit_test_mode():
    """Exit test mode by restoring original data"""
    return restore_data()

if __name__ == "__main__":
    # When run directly, generate and save test data
    load_test_mode()
    print("Test mode enabled. Test tasks and categories created.")

