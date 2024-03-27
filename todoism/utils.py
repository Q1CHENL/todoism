import curses
import todoism.print as pr
import todoism.task as tsk


indent = 7

def reid(task_list):
    for i, t in enumerate(task_list):
        t['id'] = i + 1


def is_view_fully_packed(start, end, capacity):
    """indicates whether the current view is completely filled with tasks"""
    return end - start + 1 >= capacity


def edit(stdscr, task, mode):
    """
    A editing wrapper implemented using getch(). It delivers 
    more comprehensive functionalities than getstr() does.
    """
    while True:
        y, x = stdscr.getyx()
        ch = stdscr.getch()
        if ch == 10:  # Enter to complete
            break
        elif ch == curses.KEY_LEFT:
            # cursor remains still
            stdscr.move(y, indent if x <= indent else x - 1)
        elif ch == curses.KEY_RIGHT:
            stdscr.move(y, x + 1 if x < indent +
                        len(task['description']) else indent + len(task['description']))
        elif ch == curses.KEY_BACKSPACE or ch == 127:  # delete
            if x <= indent:
                stdscr.move(y, indent)  # cursor remains still
                continue
            # -1 because deleting the char before the cursor
            task['description'] = task['description'][:x - indent - 1] + task['description'][x - indent:]
            pr.print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x - 1)
        elif 32 <= ch < 127:  # printable char
            task['description'] = task['description'][:x - indent] + chr(ch) + task['description'][x - indent:]
            pr.print_task_mode(stdscr, task, y, mode)
            stdscr.move(y, x + 1)
        elif ch == 27 and mode == pr.add_mode:
            return ""
    return task['description']

def edit_and_save(stdscr, task_list, id, row, start, end, y, x, window_height):
    stdscr.move(y, x)
    task_list[id - 1]['description'] = edit(stdscr, task_list[id - 1], pr.edit_mode)
    if task_list[id - 1]['description'] == "":
        del task_list[id - 1]
        reid(task_list)
        id, row, start, end = post_deletion_update(id, row, start, end, len(task_list) + 1, window_height)
    tsk.save_tasks(task_list, tsk.tasks_file_path)
    return id, row, start, end

def post_deletion_update(current_id, current_row, start, end, prev_task_cnt, window_height):
    """
    There are 4 senarios where the view is fully packed with tasks:
    
                                       │       │                                       │       │
    Senario 1: ┌───────┐    Senario 2: ├───────┤    Senario 3: ┌───────┐    Senario 4: ├───────┤
               ├───────┤               ├───────┤               ├───────┤               ├───────┤
               ├───────┤               ├───────┤               ├───────┤               ├───────┤   
               ├───────┤               ├───────┤               ├───────┤               ├───────┤
               └───────┘               └───────┘               ├───────┤               ├───────┤                  
                                                               │       │               │       │
    And the view update rules are similar to the Apple Reminder's
                
                
    There is only 1 senario where the view is not fully packed with tasks:
    
    Senario 5: ┌───────┐
               ├───────┤
               ├───────┤
               │       │
               └───────┘
    """
    if is_view_fully_packed(start, end, window_height - 1):
        # Senarios 1
        if window_height - 1 == prev_task_cnt:
            if current_id == end:
                current_row = current_row - 1
            end = end - 1
            if current_id > 1 and current_id == prev_task_cnt:
                current_id = current_id - 1
        # Senario 2
        elif prev_task_cnt == end and prev_task_cnt > window_height - 1:
            start = start - 1
            end = end - 1
            current_id = current_id - 1
        # Senario 3 and 4 does not lead to any change
    
    # Senario 5
    else:
        end = end - 1
        if current_id == prev_task_cnt:
            current_row = current_row - 1
            current_id = current_id - 1
    return current_id, current_row, start, end