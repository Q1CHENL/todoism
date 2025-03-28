import json
import uuid
import todoism.preference as pref
import todoism.state as st

def generate_test_tasks():
    """Generate a fresh set of test tasks with proper UUIDs and category_id"""
    test_tasks = [
        {
            "id": 1,
            "uuid": str(uuid.uuid4()),
            "description": "Implement dev mode",
            "due": "",
            "status": False,
            "flagged": True,
            "category_id": 0
        },
        {
            "id": 2,
            "uuid": str(uuid.uuid4()),
            "description": "Sort by flagged or done",
            "due": "",
            "status": True,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 3,
            "uuid": str(uuid.uuid4()),
            "description": "Auto update todoism",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 4,
            "uuid": str(uuid.uuid4()),
            "description": "Work category task example",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 1
        },
        {
            "id": 5,
            "uuid": str(uuid.uuid4()),
            "description": "Personal category task example",
            "due": "",
            "status": False,
            "flagged": True,
            "category_id": 2
        },
        {
            "id": 6,
            "uuid": str(uuid.uuid4()),
            "description": "Very long task description for testing text wrapping and scrolling behavior in the todoism terminal user interface",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 7,
            "uuid": str(uuid.uuid4()),
            "description": "Call dentist for appointment",
            "due": "",
            "status": False,
            "flagged": True,
            "category_id": 3  # Health
        },
        {
            "id": 8,
            "uuid": str(uuid.uuid4()),
            "description": "Buy groceries for the week",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 4  # Shopping
        },
        {
            "id": 9,
            "uuid": str(uuid.uuid4()),
            "description": "Finish quarterly report",
            "due": "",
            "status": True,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 10,
            "uuid": str(uuid.uuid4()),
            "description": "Research new programming language",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 11,
            "uuid": str(uuid.uuid4()),
            "description": "Plan weekend trip",
            "due": "",
            "status": False,
            "flagged": True,
            "category_id": 6  # Travel
        },
        {
            "id": 12,
            "uuid": str(uuid.uuid4()),
            "description": "Fix bathroom sink",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 7  # Home
        },
        {
            "id": 13,
            "uuid": str(uuid.uuid4()),
            "description": "Schedule team meeting",
            "due": "",
            "status": True,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 14,
            "uuid": str(uuid.uuid4()),
            "description": "Create weekly workout plan",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 15,
            "uuid": str(uuid.uuid4()),
            "description": "Read new book on productivity",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 16,
            "uuid": str(uuid.uuid4()),
            "description": "Update resume",
            "due": "",
            "status": False,
            "flagged": True,
            "category_id": 9  # Career
        },
        {
            "id": 17,
            "uuid": str(uuid.uuid4()),
            "description": "Pay monthly bills",
            "due": "",
            "status": True,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 18,
            "uuid": str(uuid.uuid4()),
            "description": "Organize digital files",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 19,
            "uuid": str(uuid.uuid4()),
            "description": "Order birthday gift for mom",
            "due": "",
            "status": False,
            "flagged": True,
            "category_id": 4  # Shopping
        },
        {
            "id": 20,
            "uuid": str(uuid.uuid4()),
            "description": "Sign up for new fitness class",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 21,
            "uuid": str(uuid.uuid4()),
            "description": "Finish home improvement project",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 7  # Home
        },
        {
            "id": 22,
            "uuid": str(uuid.uuid4()),
            "description": "Research vacation destinations",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 6  # Travel
        },
        {
            "id": 23,
            "uuid": str(uuid.uuid4()),
            "description": "Attend dental checkup",
            "due": "",
            "status": True,
            "flagged": False,
            "category_id": 3  # Health
        },
        {
            "id": 24,
            "uuid": str(uuid.uuid4()),
            "description": "Complete online course",
            "due": "",
            "status": False,
            "flagged": True,
            "category_id": 5  # Learning
        },
        {
            "id": 25,
            "uuid": str(uuid.uuid4()),
            "description": "Review annual budget",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 26,
            "uuid": str(uuid.uuid4()),
            "description": "Prepare presentation for client meeting",
            "due": "",
            "status": False, 
            "flagged": True,
            "category_id": 1  # Work
        },
        {
            "id": 27,
            "uuid": str(uuid.uuid4()),
            "description": "Another task with very long description to test horizontal scrolling and ensure proper text display in the terminal interface",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 9  # Career
        },
        {
            "id": 28,
            "uuid": str(uuid.uuid4()),
            "description": "Buy new workout equipment",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 29,
            "uuid": str(uuid.uuid4()),
            "description": "Schedule annual doctor checkup",
            "due": "",
            "status": False,
            "flagged": False,
            "category_id": 3  # Health
        },
        {
            "id": 30,
            "uuid": str(uuid.uuid4()),
            "description": "Clean garage",
            "due": "",
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

def load_dev_mode():
    """Load test tasks and categories"""
    st.is_dev_mode = True

    test_tasks = generate_test_tasks()
    test_categories = generate_test_categories()
        
    with open(pref.TEST_CATEGORIES_FILE_PATH, 'w') as file:
        json.dump(test_categories, file, indent=4)
    
    with open(pref.TEST_TASKS_FILE_PATH, 'w') as file:
        json.dump(test_tasks, file, indent=4)
    
    return True
