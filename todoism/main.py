import curses
import todoism.utils as ut
import todoism.task as tsk
import todoism.print as pr
import todoism.settings as st
import todoism.command as cmd


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
    window_height = stdscr.getmaxyx()[0]
    # print window of task id
    start = 1 if task_cnt > 0 else 0
    end = task_cnt if task_cnt < window_height - 1 else window_height - 1

    while True:
        task_cnt = len(task_list)
        done_cnt = tsk.done_count(task_list)

        stdscr.clear()
        # Selected task highlighting
        color_selected = st.get_color_selected()
        curses.init_pair(1, curses.COLOR_BLACK, color_selected)

        pr.print_main_view(
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
        window_height = stdscr.getmaxyx()[0]

        # for restoring previous view if add was interrupted
        old_start = start
        old_end = end
        # Wait for user input
        key = stdscr.getch()
        # Handle user input
        if key == ord('a'):
            curses.echo()
            curses.curs_set(1)
            # adjust start end for pre-print
            # taskoverflow if a new one is added:
            if task_cnt >= window_height - 1:
                if end <= task_cnt:
                    start = task_cnt - (end - start - 1)
                    end = task_cnt
            stdscr.erase()
            pr.print_status_bar(stdscr, done_cnt, task_cnt)
            pr.print_tasks(stdscr, task_list, current_id, start, end)
            stdscr.addstr(window_height - 1 if task_cnt >= window_height -
                          1 else task_cnt + 1, 4 if task_cnt < 9 else 3, f"{task_cnt + 1}.{' '}")
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
                current_id = new_id  # new id
                if end == task_cnt - 1 and current_row < window_height - 1:
                    current_row = current_row + 1
                else:
                    current_row = window_height - 1
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
                    window_height
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
            if task_cnt >= window_height - 1:
                stdscr.erase()
                pr.print_main_view(stdscr, len(done_list), len(task_list), task_list, current_id, start, end - 1)
            stdscr.addstr(window_height - 1, 0, ":")
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
                current_row
            )
            command_line = ""  # Clear the command line after executing the command
        elif key == curses.KEY_UP and current_id > 1:
            # current is top most task (id != 1)
            if task_cnt >= window_height - 1 and start > 1 and current_row == 1:
                start = start - 1
                end = end - 1
            else:
                current_row = current_row - 1
            current_id -= 1
        elif key == curses.KEY_DOWN and current_id < task_cnt:
            current_id += 1
            if task_cnt > window_height - 1 and current_row == window_height - 1:
                start = start + 1
                end = end + 1
            else:
                current_row = current_row + 1
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
                        window_height
                    )

                    # update task_cnt
                    task_cnt = task_cnt - 1
                tsk.save_tasks(task_list, tsk.tasks_file_path)


def run():
    curses.wrapper(main)


if __name__ == "__main__":
    run()
