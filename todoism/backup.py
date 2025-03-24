import os
import shutil

import todoism.preference as pref

BACKUP_TASKS_PATH = os.path.join(pref.CONFIG_DIR, "tasks_backup.json")
BACKUP_CATEGORIES_PATH = os.path.join(pref.CONFIG_DIR, "categories_backup.json")

def backup_data():
    """Backup normal tasks and categories"""
    try:
        success = True
        if os.path.exists(pref.get_tasks_path()):
            shutil.copy2(pref.get_tasks_path(), BACKUP_TASKS_PATH)
        else:
            success = False
        if os.path.exists(pref.get_categories_path()):
            shutil.copy2(pref.get_categories_path(), BACKUP_CATEGORIES_PATH)
        else:
            success = False            
        return success
    except Exception as e:
        print(f"Error backing up data: {e}")
        return False
