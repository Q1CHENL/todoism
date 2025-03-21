import re
import os
import argparse
import curses
import importlib.util
import todoism.task as tsk
import todoism.print as pr
import todoism.main as main

def is_dev_environment():
    """
    Detect if running in development environment by:
    1. Checking if test module exists
    2. Checking if running from source directory
    """
    # Try to find the test module
    test_spec = importlib.util.find_spec('test')
    
    # Get the package root directory
    package_root = os.path.dirname(os.path.dirname(__file__))
    
    # Check if .git exists (development) or if we're in site-packages (installed)
    is_git_repo = os.path.exists(os.path.join(package_root, '.git'))
    in_site_packages = 'site-packages' in __file__
    
    return test_spec is not None and is_git_repo and not in_site_packages

def get_active_mode():
    """Get current running mode"""
    return 'development' if is_dev_environment() else 'production'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add", metavar="TEXT", type=validate_text, help="add new todo (inside single/double quotes)")
    parser.add_argument("-d", "--delete", metavar="ID", type=validate_id, help="delete todo by id")
    parser.add_argument("-p", "--print-all", action="store_true", help="print all todos")
    parser.add_argument("-f", "--flag", action="store_true", help="set task as flagged (used with '-a')")
    parser.add_argument("-v", "--version", action="store_true", help="show todoism version")
    if is_dev_environment():
        parser.add_argument("--dev", action="store_true", help="enter development mode")
    return parser.parse_args()

def validate_id(arg):
    try:
        id_ = int(arg)
        if id_ <= 0:
            raise argparse.ArgumentTypeError(f"invalid id: {arg!r}, should be > 0")
    except:
        raise argparse.ArgumentTypeError(f"invalid id: {arg!r}, should be a number")
    else:
        return id_

def validate_text(arg):
    if not re.match(r"^\w+", arg):
        raise argparse.ArgumentTypeError(f"invalid todo text: {arg!r}")
    return arg

def run():
    args = parse_args()
    if args.add:
        tsk.add_new_task_cli(args.add, args.flag)
    elif args.delete:
        tsk.remove_task_cli(args.delete)
    elif args.print_all:
        todos = tsk.load_tasks()
        pr.print_all_cli(todos)
    elif args.version:
        pr.print_version()
    elif args.dev:
        if is_dev_environment():
            # Dev mode available
            import test.test as ts
            ts.load_dev_mode()
            curses.wrapper(main.main)
        print("Dev mode not available in installation")
    else:
        curses.wrapper(main.main)
