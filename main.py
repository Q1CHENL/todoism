import copy
import curses
from datetime import datetime
from utils import *

def main(stdscr):
    print(datetime.now())

    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()
    # Initialize color pairs
    curses.start_color()
    # Selected task highlighting
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)
    # Set up the screen
    curses.curs_set(0)
    stdscr.clear()
    # Assuming color pair 0 represents the default colors
    stdscr.bkgd(' ', curses.COLOR_BLACK | curses.A_NORMAL)

    # Define the initial todo list
    todo_list = load_tasks()
    done_list = []
    # task_cnt starts from 0
    # current_row and task_id start from 1
    current_row = 1
    task_cnt = len(todo_list) # done + undone
    done_cnt = done_count(todo_list)

    while True:
        stdscr.clear()
        print_status_bar(stdscr, done_cnt, task_cnt)
        print_tasks(stdscr, todo_list, current_row)
        stdscr.refresh()

        # Wait for user input
        key = stdscr.getch()
        # Handle user input
        if key == ord('a'):
            curses.echo()
            curses.curs_set(1)
            # Add a new task
            stdscr.addstr(task_cnt + 1, 3, f"{task_cnt + 1}. ")
            stdscr.refresh()
            new_task_description = edit(stdscr, "", add_mode)      
            if new_task_description:
                todo_list = add_new_task(new_task_description, task_cnt + 1)
                task_cnt = task_cnt + 1
            curses.curs_set(0)
            curses.noecho()
        elif key == ord("d"):
            # mark the current task as 'done'
            if todo_list:
                done_list.append(copy.copy(todo_list[current_row - 1]))
                todo_list[current_row - 1]['status'] = not todo_list[current_row - 1]['status']  
                done_cnt = done_cnt + 1 if todo_list[current_row - 1]['status'] is True else done_cnt - 1
                save_tasks(todo_list)
        elif key == ord('e'):
            curses.echo()
            curses.curs_set(1)            
            stdscr.move(current_row, len(todo_list[current_row - 1]['description']) + indent)
            todo_list[current_row - 1]['description'] = edit(stdscr, todo_list[current_row - 1]['description'], edit_mode)
            save_tasks(todo_list)
            curses.curs_set(0)
            curses.noecho()        
        elif key == ord('f'):
            todo_list[current_row - 1]['flagged'] = not todo_list[current_row - 1]['flagged'] 
        elif key == ord('h'):
            stdscr.addstr(len(done_list) + 1, 0, "Completed Tasks:")
            for i, task in enumerate(done_list):
                stdscr.addstr(len(done_list) + i + 2, 0, f"{i + 1}. {task}")
            while stdscr.getch() is not ord('h'):
                continue
        elif key == ord('q'):
            break
        elif key == curses.KEY_UP and current_row > 1:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < task_cnt:
            current_row += 1
        elif key == curses.KEY_BACKSPACE or key == 127:
            k = stdscr.getch() 
            if k == curses.KEY_BACKSPACE or k == 127:
                if task_cnt > 0:
                    task_cnt = task_cnt - 1
                    if todo_list[current_row - 1]['status'] is True:
                        done_cnt = done_cnt - 1
                    del todo_list[current_row - 1]                     
                save_tasks(todo_list)
                current_row = current_row - 1 if current_row > 1 else 1    
        elif key == ord(':'):
            curses.echo()
            curses.curs_set(1)
            stdscr.addstr(curses.LINES - 1, 0, ":")
            stdscr.refresh()
            command_line = stdscr.getstr().decode('utf-8')
            curses.curs_set(0)
            curses.noecho()
            todo_list, done_list, current_row = execute_command(stdscr, command_line, todo_list, done_list, current_row)
            command_line = ""  # Clear the command line after executing the command

if __name__ == "__main__":
    # Initialize curses
    curses.wrapper(main)
