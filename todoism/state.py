# Current selected ids
current_task_id = 1
current_category_id = 0

# Window size
latest_max_x = 0
latest_max_y = 0
old_max_x = 0
old_max_y = 0

# Max number of tasks that can be displayed
old_max_capacity = 0
latest_max_capacity = 0

# Displayed range of tasks
start_task_id = 1
end_task_id = 1

# Current row in task panel
current_task_row = 1

task_cnt = 0
cat_cnt = 0

# Current mode
adding_task = False
editing_task = False
searching = False
is_dev_mode = False

filtered_tasks = []

focus_manager = None
