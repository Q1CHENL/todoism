def search(query, task_list) -> list:
    query = query.lower()
    return [
        task for task in task_list
        if query in task["description"].lower()
    ]
