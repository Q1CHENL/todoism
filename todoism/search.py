import todoism.state as st

def search(query, task_list):
    query = query.lower()
    st.filtered_tasks = [
        task for task in task_list
        if query in task['description'].lower()
    ]
