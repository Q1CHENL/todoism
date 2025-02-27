import time
import curses
import todoism.utils as ut
import todoism.task as tsk
import todoism.print as pr
import todoism.settings as st
import todoism.command as cmd
import todoism.cli as cli


def main(stdscr):
    stdscr.keypad(True)  # enable e.g arrow keys
    stdscr.scrollok(True)
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()
    
    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    
    # Initialize color pairs
    curses.start_color()
    # progress colors
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    # regular color pair
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # Green for done symbol
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # Orange (using yellow as closest match) for flag symbol
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    # Set up the screen
    curses.curs_set(0)
    stdscr.clear()
    # Assuming color pair 0 represents the default colors
    stdscr.bkgd(' ', curses.COLOR_BLACK | curses.A_NORMAL)

    # Define the initial todo list
    task_list = tsk.load_tasks()
    done_list = []  # a part of task list
    purged_list = []

    ut.reid(task_list)  # reid in case something went wrong in last session
    task_cnt = len(task_list)  # done + undone
    done_cnt = tsk.done_count(task_list)
    current_id = 1 if task_cnt > 0 else 0 # id of task selected
    current_row = 1 if task_cnt > 0 else 0  # range: [0, height-1]
    max_capacity = stdscr.getmaxyx()[0] - 1
    # print window of task id
    start = 1 if task_cnt > 0 else 0
    end = task_cnt if task_cnt < max_capacity else max_capacity
    should_repaint = True
    
    # Set a timeout for getch() to make it non-blocking (500ms)
    stdscr.timeout(500)
    # Track when we last updated the time
    last_time_update = time.time()
    
    # Initialize key to avoid UnboundLocalError
    key = 0
    
    while True:
        task_cnt = len(task_list)
        done_cnt = tsk.done_count(task_list)
        
        # Get current window dimensions
        new_max_y, max_x = stdscr.getmaxyx()
        new_max_capacity = new_max_y - 1  # Account for status bar
        
        # Check if window height has changed and we need to adjust view
        if new_max_capacity != max_capacity:
            # Store old capacity before updating
            old_max_capacity = max_capacity
            max_capacity = new_max_capacity
            
            # If window got larger
            if max_capacity > old_max_capacity:
                # Calculate how many more tasks we can display
                additional_capacity = max_capacity - old_max_capacity
                
                # Check if we're viewing the end of the task list (common when scrolled down)
                if end == task_cnt and task_cnt > max_capacity:
                    # We're at the end of the list - keep the end fixed and adjust start
                    # to show more tasks at the beginning
                    end = task_cnt  # Keep showing the last task
                    start = max(1, end - max_capacity + 1)  # Show as many as possible
                    
                    # Adjust row to maintain the selected task position
                    if current_id >= start and current_id <= end:
                        current_row = current_id - start + 1
                else:
                    # Standard case - just expand the end to show more tasks
                    new_end = min(end + additional_capacity, task_cnt)
                    
                    # Only update if we can actually show more tasks
                    if new_end > end:
                        end = new_end
                        
            # If window got smaller and can't display current range
            elif end - start + 1 > max_capacity:
                # Try to keep current task in view by adjusting the range
                if current_id >= start and current_id <= end:
                    # Calculate middle position to keep current task visible
                    middle_offset = max_capacity // 2
                    
                    if current_id <= middle_offset:
                        # Current task is near beginning
                        start = 1
                        end = min(start + max_capacity - 1, task_cnt)
                    elif current_id > task_cnt - middle_offset:
                        # Current task is near end
                        end = task_cnt
                        start = max(1, end - max_capacity + 1)
                    else:
                        # Current task is in middle
                        start = current_id - middle_offset
                        end = start + max_capacity - 1
                
                # Ensure row position is correct
                if current_id >= start and current_id <= end:
                    current_row = current_id - start + 1
            
            # Force a repaint after window resize
            should_repaint = True
        
        # Check if we need to update the time (every second)
        current_time = time.time()
        if current_time - last_time_update >= 2.0:  # Increased to 2 seconds to reduce lag
            pr.print_status_bar(stdscr, done_cnt, task_cnt)
            stdscr.refresh()
            last_time_update = current_time
            
        # Selected task highlighting
        if should_repaint:
            color_selected = st.get_color_selected()
            curses.init_pair(1, curses.COLOR_BLACK, color_selected)
            pr.repaint(
                stdscr,
                done_cnt,
                task_cnt,
                task_list,
                current_id,
                start,
                end
            )
            
            if task_cnt == 0:
                pr.print_status_bar(stdscr, done_cnt, task_cnt)
                pr.print_msg(stdscr, pr.empty_msg)

            stdscr.refresh()
        else:
            should_repaint = True
            
        max_capacity = stdscr.getmaxyx()[0] - 1

        # for restoring previous view if add was interrupted
        old_start = start
        old_end = end
        # Wait for user input
        key = stdscr.getch()
        
        if key == -1:
            continue
            
        # Handle mouse events
        if key == curses.KEY_MOUSE:
            try:
                mouse_id, mouse_x, mouse_y, mouse_z, button_state = curses.getmouse()
                # Check if clicked on a task row (rows start at 1, status bar is at row 0)
                if 1 <= mouse_y <= min(task_cnt, max_capacity):
                    # Calculate the task ID that was clicked
                    clicked_task_row = mouse_y  # Row on screen
                    clicked_task_id = start + clicked_task_row - 1  # Actual task ID
                    
                    if 1 <= clicked_task_id <= task_cnt:
                        # Define click regions
                        status_x_start, status_x_end = 3, 4  # Status symbol at x=3
                        flag_x_start, flag_x_end = 5, 6      # Flag symbol at x=5
                        
                        # Check if clicked on status symbol (✓)
                        if status_x_start <= mouse_x <= status_x_end:
                            # Toggle task status (done/undone)
                            if task_list:
                                done_list.append(task_list[clicked_task_id - 1])
                                task_list[clicked_task_id - 1]['status'] = not task_list[clicked_task_id - 1]['status']
                                done_cnt = done_cnt + 1 if task_list[clicked_task_id - 1]['status'] is True else done_cnt - 1
                                tsk.save_tasks(task_list, tsk.tasks_file_path)
                                should_repaint = True
                        
                        # Check if clicked on flag symbol (⚑)
                        elif flag_x_start <= mouse_x <= flag_x_end:
                            # Toggle task flag
                            if task_list:
                                task_list[clicked_task_id - 1]['flagged'] = not task_list[clicked_task_id - 1]['flagged']
                                tsk.save_tasks(task_list, tsk.tasks_file_path)
                                should_repaint = True
                        
                        # Otherwise, just select the task
                        else:
                            # Update current selection
                            current_id = clicked_task_id
                            current_row = clicked_task_row
                            should_repaint = True
            except curses.error:
                # getmouse() can raise an exception if the terminal doesn't support mouse
                pass
            
        # Handle user input
        elif key == ord('a'):
            if task_cnt == ut.max_task_count:
                pr.print_msg(stdscr, pr.limit_msg)
                stdscr.refresh()
                time.sleep(1.2)
                continue
            curses.echo()
            curses.curs_set(1)
            # adjust start end for pre-print
            # taskoverflow if a new one is added:
            if task_cnt >= max_capacity:
                if end <= task_cnt:
                    start = task_cnt - (end - start - 1)
                    end = task_cnt
            stdscr.erase()
            pr.print_status_bar(stdscr, done_cnt, task_cnt)
            pr.print_tasks(stdscr, task_list, 0, start, end)
            # Add a new task with proper indentation
            new_task_num = f"{task_cnt + 1:2d}"
            stdscr.addstr(max_capacity if task_cnt >= max_capacity else task_cnt + 1, 0, f"{new_task_num} ")
            # Move cursor to the correct position after task number
            stdscr.move(max_capacity if task_cnt >= max_capacity else task_cnt + 1, ut.indent)
            stdscr.refresh()

            # Add a new task
            new_task_description = ut.edit(
                stdscr, tsk.create_new_task(task_cnt + 1), pr.add_mode)
            if new_task_description != "":
                new_id = task_cnt + 1
                task_list = tsk.add_new_task(
                    task_list, new_id, new_task_description)
                task_cnt = task_cnt + 1
                if task_cnt == 1:
                    start = 1
                if task_cnt - 1 <= max_capacity:
                    current_row = task_cnt
                else:
                    current_row = max_capacity
                current_id = new_id  # new id
                end = end + 1  # change end as well
            else:
                start = old_start
                end = old_end
            pr.print_tasks(stdscr, task_list, current_id, start, end)
            stdscr.refresh()
            curses.curs_set(0)
            curses.noecho()
        elif key == ord("d"):
            # mark the current task as 'done'
            if task_list:
                done_list.append(task_list[current_id - 1])
                task_list[current_id - 1]['status'] = not task_list[current_id - 1]['status']
                done_cnt = done_cnt + 1 if task_list[current_id - 1]['status'] is True else done_cnt - 1
                tsk.save_tasks(task_list, tsk.tasks_file_path)
        elif key == ord('e'):
            curses.echo()
            curses.curs_set(1)
            if task_cnt > 0:
                current_id, current_row, start, end = ut.edit_and_save(
                                                            stdscr,
                                                            task_list,
                                                            current_id,
                                                            current_row,
                                                            start,
                                                            end,
                                                            current_row,
                                                            len(task_list[current_id - 1]['description']) + ut.indent,
                                                            max_capacity
                                                            )
            curses.curs_set(0)
            curses.noecho()
        elif key == ord('f'):
            task_list[current_id -
                      1]['flagged'] = not task_list[current_id - 1]['flagged']
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
            
            # Disable the timeout temporarily while in command mode
            # This prevents getstr() from timing out while waiting for input
            stdscr.timeout(-1)  # -1 disables timeout completely
            
            if task_cnt >= max_capacity:
                pr.repaint(stdscr, len(done_list), len(task_list), task_list, current_id, start, end - 1)
            stdscr.addstr(max_capacity, 0, ":")
            stdscr.refresh()
            
            # Now getstr() will wait indefinitely for input
            command_line = stdscr.getstr().decode('utf-8')
            
            # Restore the timeout for the main loop
            stdscr.timeout(500)  # Back to 500ms timeout
            
            curses.curs_set(0)
            curses.noecho()
            task_list, done_list, current_id, current_row, start, end = cmd.execute_command(
                                                                          stdscr,
                                                                          command_line,
                                                                          task_list,
                                                                          done_list,
                                                                          purged_list,
                                                                          current_id,
                                                                          start,
                                                                          end,
                                                                          current_row,
                                                                          max_capacity
                                                                        )
            command_line = ""  # Clear the command line after executing the command
        elif key == curses.KEY_UP:
            start, end, current_id, current_row, should_repaint = keyup_update(     
                                                            start,
                                                            end,
                                                            current_id, 
                                                            current_row,
                                                            task_cnt,
                                                            max_capacity,
                                                            should_repaint
                                                            )
        elif key == curses.KEY_DOWN:
            start, end, current_id, current_row, should_repaint = keydown_update(
                                                            start,
                                                            end,
                                                            current_id, 
                                                            current_row,
                                                            task_cnt,
                                                            max_capacity,
                                                            should_repaint
                                                            )
        elif key == curses.KEY_BACKSPACE or key == 127:
            k = stdscr.getch()
            if k == curses.KEY_BACKSPACE or k == 127:
                # only perform deletion when task_cnt > 0
                if task_cnt > 0:
                    # update done_cnt
                    if task_list[current_id - 1]['status'] is True:
                        done_cnt = done_cnt - 1
                    # perform deletion
                    del task_list[current_id - 1]
                    # reid
                    ut.reid(task_list)
                    # view change rules are similar to apple reminder
                    current_id, current_row, start, end = ut.post_deletion_update(
                        current_id,
                        current_row,
                        start,
                        end,
                        task_cnt,
                        max_capacity
                    )

                    # update task_cnt
                    task_cnt = task_cnt - 1
                tsk.save_tasks(task_list, tsk.tasks_file_path)


def keydown_update(start, end, current_id, row, task_cnt, max_capacity, should_repaint):
    if current_id == task_cnt:
        return start, end, current_id, row, False
    current_id += 1
    if task_cnt > max_capacity and row == max_capacity:
        start = start + 1
        end = end + 1
    else:
        row = row + 1
    return start, end, current_id, row, should_repaint
                
def keyup_update(start, end, current_id, row, task_cnt, max_capacity, should_repaint):
    if current_id == 1:
        return start, end, current_id, row, False
    # current is top most task (id != 1)
    if task_cnt >= max_capacity and start > 1 and row == 1:
        start = start - 1
        end = end - 1
    else:
        row = row - 1
    current_id -= 1
    return start, end, current_id, row, should_repaint

def run():
    args = cli.parse_args()
    if args.add:
        tsk.add_new_task_cli(args.add, args.flag)
    elif args.delete:
        tsk.remove_task_cli(args.delete)
    elif args.print_all:
        todos = tsk.load_tasks()
        pr.print_all_cli(todos)
    elif args.version:
        pr.print_version()
    else:
        curses.wrapper(main)


if __name__ == "__main__":
    run()
