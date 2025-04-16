import time
import curses
import webbrowser

import todoism.task as tsk
import todoism.edit as ed
import todoism.print as pr
import todoism.message as msg
import todoism.preference as pref
import todoism.navigate as nv
import todoism.theme as thm
import todoism.keycode as kc
import todoism.category as cat
import todoism.state as st
import todoism.safe as sf

def purge(task_list, category_id=0):
    """
    purge completed tasks, appending to existing purged tasks
    """
    newly_purged = []
    remained = []
    
    def purged_cond(task, category_id):
        return task["done"] if category_id == 0 else task["done"] is True and task["category_id"] == category_id
    
    for t in st.current_cat_tasks:
        if purged_cond(t, category_id):
            newly_purged.append(t)
        else:
            remained.append(t)
            
    for t in newly_purged:
        task_list = tsk.delete_task_by_uuid(task_list, t["uuid"])
        
    tsk.reassign_task_ids(remained)
    st.current_cat_tasks = remained
    purged_tasks = tsk.load_purged_tasks()
    purged_tasks.extend(newly_purged)
    tsk.save_tasks(purged_tasks, pref.get_purged_file_path())
    return task_list

def handle_delete(task_list, task_id=0):
    task_id = st.current_task_id if task_id == 0 else task_id
    task_uuid = st.current_cat_tasks[task_id - 1].get("uuid")
    purged_tasks = tsk.load_purged_tasks()
    purged_tasks.append(st.current_cat_tasks[task_id - 1])
    tsk.save_tasks(purged_tasks, pref.get_purged_file_path())
    task_list = tsk.delete_task_by_uuid(task_list, task_uuid)
    if st.searching:
        st.current_cat_tasks = [task for task in st.current_cat_tasks if task["uuid"] != task_uuid]
    else:
        st.current_cat_tasks = tsk.get_tasks_by_category_id(task_list, st.current_category_id)
    nv.post_deletion_update(len(task_list) + 1)
    return task_list

def execute_command(stdscr, command: str, task_list: list):
    command_recognized = False    
    if command.startswith("done"):
        parts = command.split()
        if len(parts) == 2 and parts[1].isdigit():
            command_recognized = True
            id = int(parts[1])
            if 1 <= id <= len(st.current_cat_tasks):
                index = id - 1
                tsk.flip_by_key(index, "done", task_list)
            return task_list, None
        else:
            command_recognized = False
    elif command.startswith("flag"):
        parts = command.split()
        if len(parts) == 2 and parts[1].isdigit():
            command_recognized = True
            id = int(parts[1])
            if 1 <= id <= len(st.current_cat_tasks):
                index = id - 1
                tsk.flip_by_key(index, "flagged", task_list)
            return task_list, None
        else:
            command_recognized = False
    elif command == "purge":
        original_cnt = st.task_cnt
        task_list = purge(task_list,st.current_category_id)
        tsk.save_tasks(task_list)
        if len(st.current_cat_tasks) < original_cnt:
            st.current_task_id = 1
            st.current_task_row = 1
            st.start_task_id = 1
            st.end_task_id = min(len(task_list), st.latest_max_capacity)
        return task_list, None
    elif command == ("purge all"):
        task_list = purge(task_list)
        tsk.save_tasks(task_list)
        return task_list, None
    elif command.startswith("del"):
        parts = command.split()
        if len(parts) == 2 and parts[1].isdigit():
            command_recognized = True
            task_id = int(parts[1])
            if 1 <= task_id <= len(task_list):
                task_list = handle_delete(task_list, task_id)
            return task_list, None
        else:
            command_recognized = False
    elif command.startswith("edit"):
        if st.focus_manager.is_sidebar_focused():
            return task_list, None
        parts = command.split()
        if len(parts) == 2 and parts[1].isdigit():
            command_recognized = True
            task_id = int(parts[1])
            if 1 <= task_id <= len(task_list):
                st.latest_max_capacity = stdscr.getmaxyx()[0] - 1
                pr.print_task_entry(stdscr, st.current_cat_tasks[st.current_task_id-1], st.current_task_row, False, cat.SIDEBAR_WIDTH)
                st.current_task_id = int(task_id)
                st.current_task_row = st.current_task_id - st.start_task_id + 1
                if len(task_list) and st.current_task_id >= st.start_task_id and st.current_task_id <= st.end_task_id:
                    task_list = ed.handle_edit(stdscr, task_list)
                    return task_list, None
        else:
            command_recognized = False
    elif command.startswith("keycode"):
        parts = command.split()
        if len(parts) == 2:
            if parts[1] == "record":
                command_recognized = True
                stdscr.clear()
                kc.record_key_codes(stdscr)
                kc.setup_keycodes()
                return task_list, None
            elif parts[1] == "show":
                command_recognized = True
                open_keycode_summary(stdscr)
                pr.print_q_to_close(stdscr, "keycode")
                while True:
                    ch = stdscr.getch()
                    if ch == ord('q'):
                        break
                return task_list, None
        else:
            command_recognized = False
    elif command == "help":
        open_help_page(stdscr)
        st.old_max_x = st.latest_max_x
        st.old_max_y = st.latest_max_y
        old_timeout = 500
        stdscr.timeout(-1)
        while True:
            st.latest_max_y, st.latest_max_x = stdscr.getmaxyx()
            if st.latest_max_x != st.old_max_x or st.latest_max_y != st.old_max_y:
                st.old_max_x = st.latest_max_x
                st.old_max_y = st.latest_max_y
                open_help_page(stdscr)

            ch = stdscr.getch()
            if ch == ord('q'):
                stdscr.timeout(old_timeout)
                pr.clear_bottom_bar(stdscr)
                return task_list, None
            elif ch == curses.KEY_MOUSE:
                _, mouse_x, mouse_y, _, _ = curses.getmouse()
                link_y = (st.latest_max_y - len(msg.HELP_MSG.strip().split('\n'))) // 2 + 10
                link_x = (st.latest_max_x - len(msg.HELP_MSG.strip().split('\n')[0])) // 2 + 39
                link_width = len("Github page")
                if (mouse_y == link_y and 
                    link_x <= mouse_x < link_x + link_width):
                    webbrowser.open("https://github.com/Q1CHENL/todoism")
                    continue

    elif command == "pref":
        selection_index = 0
        open_pref_panel(stdscr, selection_index)
        old_timeout = 500  
        stdscr.timeout(-1)
        quit = False
        
        st.old_max_x = st.latest_max_x
        st.old_max_y = st.latest_max_y
        
        while True:
            if quit:
                pr.clear_bottom_bar(stdscr)
                break                
            # Keep selection index in valid range
            if selection_index > 12:
                selection_index = 12
            elif selection_index < 0:
                selection_index = 0
            st.latest_max_y, st.latest_max_x = stdscr.getmaxyx()
            if st.latest_max_x != st.old_max_x or st.latest_max_y != st.old_max_y:
                st.old_max_x = st.latest_max_x
                st.old_max_y = st.latest_max_y
                open_pref_panel(stdscr, selection_index)
                        
            pr.print_pref_panel(stdscr, selection_index)
            
            # Get the current preference item
            line = msg.PREF_PANEL.strip().split('\n')[selection_index + 2].strip().split(':')
            preference_type = line[0].strip()
            
            if preference_type == "│   Strikethrough":
                ch = stdscr.getch()
                if ch == kc.TAB:
                    st.strikethrough = not st.strikethrough
                    pref.set_bool_setting("strikethrough", st.strikethrough)
                    pr.print_pref_panel(stdscr, selection_index)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            
            # Handle different preference types
            elif preference_type == "│   Tag in All Tasks":
                ch = stdscr.getch()
                if ch == kc.TAB:
                    st.tag = not st.tag
                    pref.set_bool_setting("tag", st.tag)
                    pr.print_pref_panel(stdscr, selection_index)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
                    
            elif preference_type == "│   Bold Text":
                ch = stdscr.getch()
                if ch == kc.TAB:
                    st.bold_text = not st.bold_text
                    pref.set_bool_setting("bold_text", st.bold_text)
                    pr.print_pref_panel(stdscr, selection_index)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
                    
            elif preference_type == "│   Theme":
                colors = ["purple", "cyan", "blue", "red", "yellow"]
                current_color = st.theme_color
                color_index = colors.index(current_color) if current_color in colors else 0
                
                ch = stdscr.getch()
                if ch == kc.TAB:
                    color_index = (color_index + 1) % len(colors)
                    st.theme_color = colors[color_index]
                    pref.set_str_setting("selected_color", colors[color_index])
                    pr.print_pref_panel(stdscr, selection_index)
                    curses.init_pair(thm.SELECTION_COLOR_PAIR_NUM, thm.get_color_code_by_str("black"), thm.get_theme_color_curses())
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            
            elif preference_type == "│   Date format":
                ch = stdscr.getch()
                if ch == kc.TAB:
                    date_formats = ["Y-M-D", "D-M-Y", "M-D-Y"]
                    current_format = st.date_format
                    date_index = date_formats.index(current_format) if current_format in date_formats else 0
                    date_index = (date_index + 1) % len(date_formats)
                    st.date_format = date_formats[date_index]
                    pref.set_str_setting("date_format", date_formats[date_index])
                    pr.print_pref_panel(stdscr, selection_index)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            
            elif preference_type.startswith("│   Sort by flagged"):
                ch = stdscr.getch()
                if ch == kc.TAB:
                    st.sort_by_flagged = not st.sort_by_flagged
                    pref.set_bool_setting("sort_by_flagged", st.sort_by_flagged)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
                    
            elif preference_type.startswith("│   Sort by done"):
                ch = stdscr.getch()
                if ch == kc.TAB:
                    st.sort_by_done = not st.sort_by_done
                    pref.set_bool_setting("sort_by_done", st.sort_by_done)
                elif ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
            # Handle any other preference types or empty lines
            else:
                ch = stdscr.getch()
                if ch == curses.KEY_UP:
                    selection_index -= 2
                elif ch == curses.KEY_DOWN:
                    selection_index += 2
                elif ch == ord('q'):
                    quit = True
        # Restore original timeout
        stdscr.timeout(old_timeout)
        return task_list, None
    
    elif command.strip() == "":
        return task_list, None

    if not command_recognized and command.strip():
        error_msg = f"Invalid command: '{command}'. Type command 'help' for help."
        # Clear the line first, error might occur if resized small
        sf.safe_move(stdscr, st.latest_max_y - 2, 1)
        pr.clear_bottom_bar_except_status(stdscr)
        attr = thm.get_color_pair_by_str("red") | curses.A_BOLD
        sf.safe_addstr(stdscr, st.latest_max_y - 2, 1, error_msg, attr)
        stdscr.refresh()
        time.sleep(1.5)
        # Clear the error message
        sf.safe_move(stdscr, st.latest_max_y - 2, 1)
        pr.clear_bottom_bar_except_status(stdscr)
        stdscr.refresh()

    return task_list, None

def open_help_page(stdscr):
    stdscr.clear()
    pr.print_outer_frame(stdscr)
    pr.print_msg(stdscr, msg.HELP_MSG)
    pr.print_q_to_close(stdscr, "help")

def open_pref_panel(stdscr, selection_index):
    stdscr.clear()
    pr.print_pref_panel(stdscr, selection_index)
    pr.print_outer_frame(stdscr)
    pr.print_q_to_close(stdscr, "preferences")

def open_keycode_summary(stdscr):
    stdscr.clear()
    pr.print_msg(stdscr, msg.keycode_summary())
    pr.print_outer_frame(stdscr)
    pr.print_q_to_close(stdscr, "keycode")