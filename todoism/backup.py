import os
import shutil
import todoism.preference as pref

# Backup file paths
backup_file_path = os.path.join(pref.config_dir, "tasks_backup.json")
backup_categories_path = os.path.join(pref.config_dir, "categories_backup.json")

def backup_normal_data():
    """Backup normal tasks and categories (not test data)"""
    try:
        success = True
        
        if os.path.exists(pref.tasks_file_path):
            shutil.copy2(pref.tasks_file_path, backup_file_path)
        else:
            success = False
            
        if os.path.exists(pref.categories_file_path):
            shutil.copy2(pref.categories_file_path, backup_categories_path)
        else:
            success = False
            
        return success
    except Exception as e:
        print(f"Error backing up data: {e}")
        return False

def restore_normal_data():
    """Restore normal tasks and categories from backup"""
    try:
        success = True
        
        # Restore normal files
        if os.path.exists(backup_file_path):
            shutil.copy2(backup_file_path, pref.tasks_file_path)
            os.remove(backup_file_path)
        else:
            success = False
            
        if os.path.exists(backup_categories_path):
            shutil.copy2(backup_categories_path, pref.categories_file_path)
            os.remove(backup_categories_path)
        else:
            success = False
            
        return success
    except Exception as e:
        print(f"Error restoring data: {e}")
        return False