import re
from datetime import datetime
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
    ]

    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            due_date = match.group(1) if match.groups() else match.group(0).strip("[]")
            remaining_text = description[:match.start()] + description[match.end():]
            return due_date, remaining_text.strip()

    return "", description.strip()


def add_due_key_if_missing(task_list: list):
    """
    Add a 'due' key with an empty string value to each task
    in the list if the 'due' key is not present.
    """
    for task in task_list:
        if "due" not in task:
            task["due"] = ""

def is_due_today(date_str: str) -> bool:
    """
    Checks if a date string in any supported format represents today's date.
    
    Supported formats:
    - yyyy-mm-dd hh:mm
    - yyyy-mm-dd
    - mm-dd hh:mm
    - mm-dd or dd-mm
    - hh:mm (implicitly today)
    
    Args:
        date_str: The date string to check
        
    Returns:
        True if the date represents today, False otherwise
    """
    if date_str == "":
        return False
        
    # Get today's date components for comparison
    today = datetime.now().date()
    today_year = today.year
    today_month = today.month
    today_day = today.day
    
    try:
        # Case 1: Time-only format (hh:mm)
        if len(date_str) == 5 and ":" in date_str:
            return True  # Time-only implies today
            
        # Case 2: Full datetime (yyyy-mm-dd hh:mm)
        if len(date_str) == 16 and date_str[4] == '-' and date_str[7] == '-' and date_str[10] == ' ':
            year = int(date_str[0:4])
            month = int(date_str[5:7])
            day = int(date_str[8:10])
            return year == today_year and month == today_month and day == today_day
            
        # Case 3: Full date (yyyy-mm-dd)
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            year = int(date_str[0:4])
            month = int(date_str[5:7])
            day = int(date_str[8:10])
            return year == today_year and month == today_month and day == today_day
            
        # Case 4: mm-dd hh:mm
        if len(date_str) >= 11 and "-" in date_str and ":" in date_str:
            parts = date_str.split(" ")[0].split("-")
            month = int(parts[0])
            day = int(parts[1])
            return month == today_month and day == today_day
            
        # Case 5: Ambiguous mm-dd or dd-mm
        if "-" in date_str and len(date_str.split("-")) == 2:
            parts = date_str.split("-")
            # Try mm-dd interpretation
            if 1 <= int(parts[0]) <= 12 and 1 <= int(parts[1]) <= 31:
                if int(parts[0]) == today_month and int(parts[1]) == today_day:
                    return True
            # Try dd-mm interpretation
            if 1 <= int(parts[1]) <= 12 and 1 <= int(parts[0]) <= 31:
                if int(parts[1]) == today_month and int(parts[0]) == today_day:
                    return True
            return False
            
    except (ValueError, IndexError):
        # Handle any parsing errors
        return False
        
    return False

def get_due_str(task):
    due_str = task["due"]
    due_len = len(due_str)

    if is_due_today(due_str):
        due_str = "Today"
        if due_len == 16 or due_len == 11 or (due_len == 5 and task["due"][2] == ':'):
            due_str += ' ' + task["due"][-5:]
    
    if due_str != "":
        due_str = '[' + due_str + ']'
    
    return due_str