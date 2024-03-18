import curses
from .utils import *
# import structure:
# print and task are imported in utils
# utils is imported in main

def main():
    global task_highlighting_color
    stdscr = curses.initscr()
    stdscr.keypad(True) # enable e.g arrow keys
    # todo save settings like color in a json file
    stdscr.scrollok(True)
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()
    # Initialize color pairs
    curses.start_color()
    # progress colors
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK) # regular color pair
    # Set up the screen
    curses.curs_set(0)
    stdscr.clear()
    # Assuming color pair 0 represents the default colors
    stdscr.bkgd(' ', curses.COLOR_BLACK | curses.A_NORMAL)

    # Define the initial todo list
    task_list = load_tasks()
    done_list = [] # a  part of task list
    purged_list = []

    # task_cnt starts from 0
    # current_id and task_id start from 1
    current_id = 1
    task_cnt = len(task_list) # done + undone
    done_cnt = done_count(task_list)
    window_height = stdscr.getmaxyx()[0]    
    # print window of task id
    start = 1 if task_cnt > 0 else 0
    end = task_cnt if task_cnt < window_height - 1 else window_height - 1
    
    while True:
        stdscr.clear()
        # Selected task highlighting
        curses.init_pair(1, curses.COLOR_BLACK, task_highlighting_color)

        print_status_bar(stdscr, done_cnt, task_cnt)
        print_tasks(stdscr, task_list, current_id, start, end)
        stdscr.refresh()
        window_height = stdscr.getmaxyx()[0]

        # Wait for user input
        key = stdscr.getch()
        # Handle user input
        if key == ord('a'):
            curses.echo()
            curses.curs_set(1)
            if task_cnt >= window_height - 1:
                start = task_cnt - (end - start - 1)
                end = task_cnt
            else:
                end = end + 1
            stdscr.erase()
            print_status_bar(stdscr, done_cnt, task_cnt)
            print_tasks(stdscr, task_list, current_id, start, end)
            stdscr.addstr(window_height - 1 if task_cnt >= window_height - 1 else task_cnt + 1, 3, f"{task_cnt + 1}.{' ' if task_cnt + 1 >= 10 else ' ' * 2}")
            stdscr.refresh()
            
            # Add a new task
            new_task_description = edit(stdscr, create_new_task(task_cnt + 1), add_mode)               
            if new_task_description:
                new_id = task_cnt + 1
                task_list = add_new_task(task_list, new_id, new_task_description)
                task_cnt = task_cnt + 1
                end = end + 1 # change end as well
                if task_cnt == 1:
                    start = 1
                current_id = new_id # new id
            print_tasks(stdscr, task_list, current_id, start, end)
            stdscr.refresh()  
            curses.curs_set(0)
            curses.noecho()
        elif key == ord("d"):
            # mark the current task as 'done'
            if task_list:
                done_list.append(task_list[current_id - 1])
                task_list[current_id - 1]['status'] = not task_list[current_id - 1]['status']  
                done_cnt = done_cnt + 1 if task_list[current_id - 1]['status'] is True else done_cnt - 1
                save_tasks(task_list, tasks_file_path)
        elif key == ord('e'):
            curses.echo()
            curses.curs_set(1)
            stdscr.move(current_id if current_id <= window_height - 1 else window_height - 1, len(task_list[current_id - 1]['description']) + indent)
            task_list[current_id - 1]['description'] = edit(stdscr, task_list[current_id - 1], edit_mode)
            # delete the task if it was edited to empty
            if task_list[current_id - 1]['description'] == "":
                del task_list[current_id - 1]
                reid(task_list)
            save_tasks(task_list, tasks_file_path)
            curses.curs_set(0)
            curses.noecho()        
        elif key == ord('f'):
            task_list[current_id - 1]['flagged'] = not task_list[current_id - 1]['flagged'] 
        elif key == ord('h'):
            stdscr.addstr(len(done_list) + 1, 0, "Completed Tasks:")
            for i, task in enumerate(done_list):
                stdscr.addstr(len(done_list) + i + 2, 0, f"{i + 1}. {task}")
            while stdscr.getch() is not ord('h'):
                continue
        elif key == ord('q'):
            break
        elif key == ord(':'):
            curses.echo()
            curses.curs_set(1)
            stdscr.addstr(curses.LINES - 1, 0, ":")
            stdscr.refresh()
            command_line = stdscr.getstr().decode('utf-8')
            curses.curs_set(0)
            curses.noecho()
            task_list, done_list, current_id, task_highlighting_color = execute_command(stdscr, command_line, task_list, done_list, purged_list, current_id)
            command_line = ""  # Clear the command line after executing the command
        elif key == curses.KEY_UP and current_id > 1:
            current_id -= 1
            if task_cnt > window_height - 1 and start > 1:
                start = start - 1
                end = end - 1
        elif key == curses.KEY_DOWN and current_id < task_cnt:
            current_id += 1
            if task_cnt > window_height - 1 and current_id > window_height - 1:
                start = start + 1
                end = end + 1
        elif key == curses.KEY_BACKSPACE or key == 127:
            k = stdscr.getch() 
            if k == curses.KEY_BACKSPACE or k == 127:
                if task_cnt > 0:
                    task_cnt = task_cnt - 1
                    if task_list[current_id - 1]['status'] is True:
                        done_cnt = done_cnt - 1
                    del task_list[current_id - 1]
                    for t in task_list[current_id - 1:]:
                        t['id'] = t['id'] - 1                     
                save_tasks(task_list, tasks_file_path)
                current_id = current_id - 1 if current_id > 1 else 1    
        task_cnt = len(task_list)
        done_cnt = done_count(task_list)

if __name__ == "__main__":
    main()
