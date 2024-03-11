import os
import json
import copy
import curses
from datetime import datetime

home_dir = os.path.expanduser("~")
config_dir = os.path.join(home_dir, ".todoism")
os.makedirs(config_dir, exist_ok=True)
tasks_file_path = os.path.join(config_dir, "tasks.json")

def load_tasks():
    try:
        with open(tasks_file_path, 'r') as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []
    return tasks

def add_new_task(task_description):
    new_task = {
        'task': task_description,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'status': False,
        'flagged': False
    }
    tasks = load_tasks()
    tasks.append(new_task)
    # save the newly added task
    with open(tasks_file_path, 'w') as file:
        json.dump(tasks, file, indent=2)
    return tasks

def save_tasks(tasks):
    with open(tasks_file_path, 'w') as file:
        json.dump(tasks, file, indent=2)
    

def execute_command(command, todo_list, done_list, current_row, show_hidden):
    if command.startswith("add "):
        new_task = command[4:]
        if new_task:
            todo_list.append({'task': new_task, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'status': False})
    elif command.startswith("delete "):
        index_to_delete = int(command[7:]) - 1
        if 0 <= index_to_delete < len(todo_list):
            done_list.append(copy.copy(todo_list[index_to_delete]))
            todo_list[index_to_delete]['status'] = not todo_list[index_to_delete]['status']
    elif command == "toggle_hidden":
        show_hidden = not show_hidden

    return todo_list, done_list, show_hidden

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
    # todo_list = [{'task': "Make a todo list cli with an interactive panel",
    #               'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
    #               'status': False,
    #               'flagged': False
    #               }, 
    #              {'task': "Get prepare for retake exams",
    #               'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
    #               'status': False,
    #               'flagged': False
    #               }]
    done_list = []
    current_row = 0
    show_hidden = False

    while True:
        stdscr.clear()

        # Display the todo list
        for i, task in enumerate(todo_list):
            if i == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(i, 0, f"{'✅' if task['status'] else '  '} {i + 1}. {task['task'] + (75-len(task['task'])) * ' ' + task['date']} {'🚩' if task['flagged'] else ''}")
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(i, 0, f"{'✅' if task['status'] else '  '} {i + 1}. {task['task'] + (75-len(task['task'])) * ' ' + task['date']} {'🚩' if task['flagged'] else ''}" )
        if show_hidden:
            stdscr.addstr(len(todo_list) + 1, 0, "Completed Tasks:")
            for i, task in enumerate(done_list):
                stdscr.addstr(len(todo_list) + i + 2, 0, f"{i + 1}. {task}")

        # Refresh the screen
        stdscr.refresh()

        # Wait for user input
        key = stdscr.getch()
        # Handle user input
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(todo_list) - 1:
            current_row += 1
        elif key == ord("a"):
            curses.echo()
            curses.curs_set(1)
            # Add a new task
            stdscr.addstr(len(todo_list), 0, f"{len(todo_list) + 1}.")
            stdscr.refresh()
            new_task = stdscr.getstr().decode('utf-8')
            if new_task:
                todo_list = add_new_task(new_task)
                # todo_list.append({'task': ' ' + new_task, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'status': False, 'flagged': False})
            curses.curs_set(0)
            curses.noecho()
        elif key == ord("d"):
            # Delete the selected task
            if todo_list:
                done_list.append(copy.copy(todo_list[current_row]))
                # del todo_list[current_row]
                todo_list[current_row]['status'] = not todo_list[current_row]['status']  
                # if current_row > 0:
                #     current_row -= 1
        elif key == ord('h'):
            show_hidden = not show_hidden
        elif key == ord('f'):
            todo_list[current_row]['flagged'] = not todo_list[current_row]['flagged'] 
        elif key == ord('e'):
            curses.echo()
            curses.curs_set(1)
            stdscr.move(current_row, len(todo_list[current_row]['task']) + 6)
            while True:
                edit_key = stdscr.getch()
                if edit_key == 10: # newline
                    save_tasks(todo_list)
                    break
                elif edit_key == curses.KEY_BACKSPACE or edit_key == 127:
                    todo_list[current_row]['task'] = todo_list[current_row]['task'][:-1]
                    stdscr.delch()
                    stdscr.move(current_row, len(todo_list[current_row]['task']) + 6)
                elif 32 <= edit_key < 127:
                    todo_list[current_row]['task'] = todo_list[current_row]['task'] + chr(edit_key)
                    # stdscr.addch(edit_key)
                    stdscr.move(current_row, len(todo_list[current_row]['task']) + 6)        
            curses.curs_set(0)
            curses.noecho()        
            
        elif key == ord(":"):
            curses.echo()
            curses.curs_set(1)
            stdscr.addstr(curses.LINES - 1, 0, ":")
            stdscr.refresh()
            command_line = stdscr.getstr().decode('utf-8')
            curses.curs_set(0)
            curses.noecho()
            todo_list, done_list, show_hidden = execute_command(command_line, todo_list, done_list, current_row, show_hidden)
            command_line = ""  # Clear the command line after executing the command
        elif key == ord("q"):
            break


if __name__ == "__main__":
    # Initialize curses
    curses.wrapper(main)
