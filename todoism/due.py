import re
from typing import Tuple

def parse_due_date(description: str) -> Tuple[str, str]:
    """
    Parses a task description to extract a due date/time in the formats:
    [yyyy-mm-dd hh:mm], [yyyy-mm-dd], [mm-dd], [hh:mm], [Tomorrow], [Next Week].
    
    Returns:
    - A tuple (due_date, remaining_text), where:
        - due_date is the extracted date as a string, or an empty string if not found.
        - remaining_text is the input string with the date removed.
    """
    patterns = [
        r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]',       # [yyyy-mm-dd hh:mm]
        r'\[(\d{4}-\d{1,2}-\d{1,2})\]',               # [yyyy-mm-dd]
        r'\[(\d{2}-\d{2} \d{2}:\d{2})\]',             # [mm-dd hh:mm]
        r'\[(\d{1,2}-\d{1,2})\]',                     # [mm-dd] or [dd-mm]
        r'\[(\d{2}:\d{2})\]',                         # [hh:mm]
        r'\[Tomorrow\]',                              # [Tomorrow]
        r'\[Next Week\]'                              # [Next Week]
    ]

    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            due_date = match.group(1) if match.groups() else match.group(0).strip("[]")
            remaining_text = description[:match.start()] + description[match.end():]
            return due_date, remaining_text.strip()  # Trim extra spaces

    return "", description.strip()


def add_due_key_if_missing(task_list: list):
    """
    Add a 'due' key with an empty string value to each task
    in the list if the 'due' key is not present.
    """
    for task in task_list:
        if "due" not in task:
            task["due"] = ""
