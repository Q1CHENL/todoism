import re
from typing import Optional

def parse_due_date(description: str) -> str:
    """
    Parse the task description to find a date in the formats:
    [yyyy-mm-dd hh:mm], [yyyy-mm-dd], [hh:mm], [Tomorrow], [Next Week]
    """
    patterns = [
        r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]',  # [yyyy-mm-dd hh:mm]
        r'\[(\d{4}-\d{2}-\d{2})\]',              # [yyyy-mm-dd]
        r'\[(\d{1,2}):(\d{2})\]',                # [hh:mm] with 1 or 2 digits for hours
        r'\[Tomorrow\]',                          # [Tomorrow]
        r'\[Next Week\]'                          # [Next Week]
    ]
    
    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            if len(match.groups()) == 1:
                return match.group(1)  # Return the captured full match
            elif len(match.groups()) == 2:
                # Format hours and minutes properly
                hours = match.group(1).zfill(2)
                minutes = match.group(2)
                return f"{hours}:{minutes}"
            else:
                return match.group(0).strip("[]")  # Remove brackets for special cases

    return ""

def add_due_key_if_missing(task_list: list):
    """
    Add a 'due' key with an empty string value to each task
    in the list if the 'due' key is not present.
    """
    for task in task_list:
        if "due" not in task:
            task["due"] = ""