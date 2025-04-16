import json
import os
from pathlib import Path
from test import generate_test_tasks, generate_test_categories, generate_test_settings

# Generate test data
test_tasks = generate_test_tasks()
test_categories = generate_test_categories()
test_settings = generate_test_settings()

# Ensure output directory exists
out_dir = Path(".todoism")
out_dir.mkdir(exist_ok=True)

# Define filenames and data
files = {
    "tasks.json": test_tasks,
    "categories.json": test_categories,
    "settings.json": test_settings,
}

# Write files and set permissions
for filename, data in files.items():
    path = out_dir / filename
    path.write_text(json.dumps(data, indent=4))
    os.chmod(path, 0o644)  # rw-r--r--
