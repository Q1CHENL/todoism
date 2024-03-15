import json
from datetime import datetime


def dump_test():
    # Dump the tasks into a JSON file
    with open('test.json', 'w') as json_file:
        json.dump(test_tasks, json_file, indent=4)

# Define the tasks
test_tasks = [
    {
        "id": 1,
        "description": "first description",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": False,
        "flagged": False
    },
    {
        "id": 2,
        "description": "second description",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": False,
        "flagged": False
    },
    {
        "id": 3,
        "description": "third description",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": False,
        "flagged": False
    },
    {
        "id": 4,
        "description": "fourth description",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": False,
        "flagged": False
    },
    {
        "id": 5,
        "description": "fifth description",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": False,
        "flagged": False
    },
    {
        "id": 6,
        "description": "sixth description",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": False,
        "flagged": False
    },
    {
        "id": 7,
        "description": "seventh description",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": False,
        "flagged": False
    }
]

