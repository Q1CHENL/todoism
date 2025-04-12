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
            "done": False,
            "flagged": True,
            "category_id": 0
        },
        {
            "id": 2,
            "uuid": str(uuid.uuid4()),
            "description": "Sort by flagged or done",
            "due": "",
            "done": True,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 3,
            "uuid": str(uuid.uuid4()),
            "description": "Auto update todoism",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 4,
            "uuid": str(uuid.uuid4()),
            "description": "Work category task example",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 1
        },
        {
            "id": 5,
            "uuid": str(uuid.uuid4()),
            "description": "Personal category task example",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 2
        },
        {
            "id": 6,
            "uuid": str(uuid.uuid4()),
            "description": "Very long task description for testing text wrapping and scrolling behavior in the todoism terminal user interface",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 7,
            "uuid": str(uuid.uuid4()),
            "description": "Call dentist for appointment",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 3  # Health
        },
        {
            "id": 8,
            "uuid": str(uuid.uuid4()),
            "description": "Buy groceries for the week",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 4  # Shopping
        },
        {
            "id": 9,
            "uuid": str(uuid.uuid4()),
            "description": "Finish quarterly report",
            "due": "",
            "done": True,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 10,
            "uuid": str(uuid.uuid4()),
            "description": "Research new programming language",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 11,
            "uuid": str(uuid.uuid4()),
            "description": "Plan weekend trip",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 6  # Travel
        },
        {
            "id": 12,
            "uuid": str(uuid.uuid4()),
            "description": "Fix bathroom sink",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 7  # Home
        },
        {
            "id": 13,
            "uuid": str(uuid.uuid4()),
            "description": "Schedule team meeting",
            "due": "",
            "done": True,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 14,
            "uuid": str(uuid.uuid4()),
            "description": "Create weekly workout plan",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 15,
            "uuid": str(uuid.uuid4()),
            "description": "Read new book on productivity",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 16,
            "uuid": str(uuid.uuid4()),
            "description": "Update resume",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 9  # Career
        },
        {
            "id": 17,
            "uuid": str(uuid.uuid4()),
            "description": "Pay monthly bills",
            "due": "",
            "done": True,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 18,
            "uuid": str(uuid.uuid4()),
            "description": "Organize digital files",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 0
        },
        {
            "id": 19,
            "uuid": str(uuid.uuid4()),
            "description": "Order birthday gift for mom",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 4  # Shopping
        },
        {
            "id": 20,
            "uuid": str(uuid.uuid4()),
            "description": "Sign up for new fitness class",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 21,
            "uuid": str(uuid.uuid4()),
            "description": "Finish home improvement project",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 7  # Home
        },
        {
            "id": 22,
            "uuid": str(uuid.uuid4()),
            "description": "Research vacation destinations",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 6  # Travel
        },
        {
            "id": 23,
            "uuid": str(uuid.uuid4()),
            "description": "Attend dental checkup",
            "due": "",
            "done": True,
            "flagged": False,
            "category_id": 3  # Health
        },
        {
            "id": 24,
            "uuid": str(uuid.uuid4()),
            "description": "Complete online course",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 5  # Learning
        },
        {
            "id": 25,
            "uuid": str(uuid.uuid4()),
            "description": "Review annual budget",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 26,
            "uuid": str(uuid.uuid4()),
            "description": "Prepare presentation for client meeting",
            "due": "",
            "done": False, 
            "flagged": True,
            "category_id": 1  # Work
        },
        {
            "id": 27,
            "uuid": str(uuid.uuid4()),
            "description": "Another task with very long description to test horizontal scrolling and ensure proper text display in the terminal interface",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 9  # Career
        },
        {
            "id": 28,
            "uuid": str(uuid.uuid4()),
            "description": "Buy new workout equipment",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 29,
            "uuid": str(uuid.uuid4()),
            "description": "Schedule annual doctor checkup",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 3  # Health
        },
        {
            "id": 30,
            "uuid": str(uuid.uuid4()),
            "description": "Clean garage",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 7  # Home
        },
        {
            "id": 31,
            "uuid": str(uuid.uuid4()),
            "description": "Prepare for the upcoming presentation",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 32,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a family gathering",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 10  # Family
        },
        {
            "id": 33,
            "uuid": str(uuid.uuid4()),
            "description": "Schedule a car maintenance appointment",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 3  # Health
        },
        {
            "id": 34,
            "uuid": str(uuid.uuid4()),
            "description": "Buy ingredients for dinner",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 4  # Shopping
        },
        {
            "id": 35,
            "uuid": str(uuid.uuid4()),
            "description": "Complete online course module",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 5  # Learning
        },
        {
            "id": 36,
            "uuid": str(uuid.uuid4()),
            "description": "Book flight tickets for vacation",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 6  # Travel
        },
        {
            "id": 37,
            "uuid": str(uuid.uuid4()),
            "description": "Organize workspace",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 7  # Home
        },
        {
            "id": 38,
            "uuid": str(uuid.uuid4()),
            "description": "Research new health trends",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 3  # Health
        },
        {
            "id": 39,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a weekend trip",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 6  # Travel
        },
        {
            "id": 40,
            "uuid": str(uuid.uuid4()),
            "description": "Attend a workshop on productivity",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 41,
            "uuid": str(uuid.uuid4()),
            "description": "Update personal budget",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 13  # Finance
        },
        {
            "id": 42,
            "uuid": str(uuid.uuid4()),
            "description": "Finish reading a book",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 43,
            "uuid": str(uuid.uuid4()),
            "description": "Prepare for a job interview",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 9  # Career
        },
        {
            "id": 44,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a surprise party",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 10  # Family
        },
        {
            "id": 45,
            "uuid": str(uuid.uuid4()),
            "description": "Create a workout schedule",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 46,
            "uuid": str(uuid.uuid4()),
            "description": "Attend a networking event",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 9  # Career
        },
        {
            "id": 47,
            "uuid": str(uuid.uuid4()),
            "description": "Visit a museum",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 6  # Travel
        },
        {
            "id": 48,
            "uuid": str(uuid.uuid4()),
            "description": "Start a new hobby",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 49,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a family vacation",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 6  # Travel
        },
        {
            "id": 50,
            "uuid": str(uuid.uuid4()),
            "description": "Organize a community event",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 51,
            "uuid": str(uuid.uuid4()),
            "description": "Create a vision board",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 52,
            "uuid": str(uuid.uuid4()),
            "description": "Attend a cooking class",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 5  # Learning
        },
        {
            "id": 53,
            "uuid": str(uuid.uuid4()),
            "description": "Volunteer for a local charity",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 54,
            "uuid": str(uuid.uuid4()),
            "description": "Join a book club",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 55,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a family reunion",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 2  # Personal
        },
        {
            "id": 56,
            "uuid": str(uuid.uuid4()),
            "description": "Create a personal website",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 9  # Career
        },
        {
            "id": 57,
            "uuid": str(uuid.uuid4()),
            "description": "Attend a fitness class",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 58,
            "uuid": str(uuid.uuid4()),
            "description": "Start a blog",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 59,
            "uuid": str(uuid.uuid4()),
            "description": "Create a meal plan",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 4  # Shopping
        },
        {
            "id": 60,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a weekend getaway",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 6  # Travel
        },
        {
            "id": 61,
            "uuid": str(uuid.uuid4()),
            "description": "Attend a seminar on personal finance",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 62,
            "uuid": str(uuid.uuid4()),
            "description": "Create a scrapbook",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 63,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a road trip",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 6  # Travel
        },
        {
            "id": 64,
            "uuid": str(uuid.uuid4()),
            "description": "Attend a workshop on coding",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 65,
            "uuid": str(uuid.uuid4()),
            "description": "Create a family photo album",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 2  # Personal
        },
        {
            "id": 66,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a charity event",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 1  # Work
        },
        {
            "id": 67,
            "uuid": str(uuid.uuid4()),
            "description": "Attend a yoga class",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 8  # Fitness
        },
        {
            "id": 68,
            "uuid": str(uuid.uuid4()),
            "description": "Create a personal development plan",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 5  # Learning
        },
        {
            "id": 69,
            "uuid": str(uuid.uuid4()),
            "description": "Plan a family movie night",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 2  # Personal
        },
        {
            "id": 70,
            "uuid": str(uuid.uuid4()),
            "description": "Organize a neighborhood clean-up",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 1  # Work
        },
        {
            "id": 71,
            "uuid": str(uuid.uuid4()),
            "description": "Learn a new programming language",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 15  # Technology
        },
        {
            "id": 72,
            "uuid": str(uuid.uuid4()),
            "description": "Participate in a community clean-up",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 11  # Community
        },
        {
            "id": 73,
            "uuid": str(uuid.uuid4()),
            "description": "Start a garden",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 16  # Environment
        },
        {
            "id": 74,
            "uuid": str(uuid.uuid4()),
            "description": "Enroll in a public speaking course",
            "due": "",
            "done": False,
            "flagged": True,
            "category_id": 18  # Education
        },
        {
            "id": 75,
            "uuid": str(uuid.uuid4()),
            "description": "Adopt a pet from a shelter",
            "due": "",
            "done": False,
            "flagged": False,
            "category_id": 19  # Pets
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
        },
        {
            "id": 10,
            "name": "Family"
        },
        {
            "id": 11,
            "name": "Community"
        },
        {
            "id": 12,
            "name": "Hobbies"
        },
        {
            "id": 13,
            "name": "Finance"
        },
        {
            "id": 14,
            "name": "Self-Care"
        },
        {
            "id": 15,
            "name": "Technology"
        },
        {
            "id": 16,
            "name": "Environment"
        },
        {
            "id": 17,
            "name": "Social"
        },
        {
            "id": 18,
            "name": "Education"
        },
        {
            "id": 19,
            "name": "Pets"
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
