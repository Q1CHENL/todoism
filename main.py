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
    current_row = 0
    show_hidden = False

    while True:
        stdscr.clear()

        # Display the todo list
        for i, task in enumerate(todo_list):
            if i == current_row:
                stdscr.attron(curses.color_pair(1))
                print_task(stdscr, task, i)
                stdscr.attroff(curses.color_pair(1))
            else:
                print_task(stdscr, task, i)
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
        elif key == ord("d"):
            # Delete the selected task
            if todo_list:
                done_list.append(copy.copy(todo_list[current_row]))
                # del todo_list[current_row]
                todo_list[current_row]['status'] = not todo_list[current_row]['status']  
        elif key == ord('h'):
            show_hidden = not show_hidden
        elif key == ord('f'):
            todo_list[current_row]['flagged'] = not todo_list[current_row]['flagged'] 
        elif key == curses.KEY_BACKSPACE or key == 127:
            k = stdscr.getch() 
            if k == curses.KEY_BACKSPACE or k == 127:
                # delete the current task
                todo_list = [t for i, t in enumerate(todo_list) if i is not current_row]
                save_tasks(todo_list)
                current_row = current_row - 1 if current_row > 0 else 0    
        elif key == ord("a"):
            curses.echo()
            curses.curs_set(1)
            # Add a new task
            stdscr.addstr(len(todo_list), 3, f"{len(todo_list) + 1}.")
            stdscr.refresh()
            new_task = edit(stdscr, "", add_mode)      
            if new_task:
                todo_list = add_new_task(new_task)
            curses.curs_set(0)
            curses.noecho()
        elif key == ord('e'):
            curses.echo()
            curses.curs_set(1)            
            stdscr.move(current_row, len(todo_list[current_row]['description']) + indent)
            todo_list[current_row]['description'] = edit(stdscr, todo_list[current_row]['description'], edit_mode)
            save_tasks(todo_list)
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
            todo_list, done_list, current_row, show_hidden = execute_command(command_line, todo_list, done_list, current_row, show_hidden)
            command_line = ""  # Clear the command line after executing the command
        elif key == ord("q"):
            break


if __name__ == "__main__":
    # Initialize curses
    curses.wrapper(main)
