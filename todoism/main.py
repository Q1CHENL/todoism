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
    # Initialize color pairs
    curses.start_color()
    # progress colors
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    # regular color pair
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
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
    
    while True:
        task_cnt = len(task_list)
        done_cnt = tsk.done_count(task_list)
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
            
            # siderbar_win = curses.newwin(height_task_win, width_siderbar_win, 0, 0)
            # siderbar_win.addstr("hello from sidebar\n");
            # siderbar_win.refresh()
    
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
        # Handle user input
        if key == ord('a'):
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
            pr.print_tasks(stdscr, task_list, current_id, start, end)
            stdscr.addstr(max_capacity if task_cnt >= max_capacity else task_cnt + 1, 4 if task_cnt < 9 else 3, f"{task_cnt + 1}.{' '}")
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
            if task_cnt >= max_capacity:
                pr.repaint(stdscr, len(done_list), len(task_list), task_list, current_id, start, end - 1)
            stdscr.addstr(max_capacity, 0, ":")
            stdscr.refresh()
            command_line = stdscr.getstr().decode('utf-8')
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
