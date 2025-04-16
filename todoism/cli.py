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
    test_module = importlib.util.find_spec("test")
    package_root = os.path.dirname(os.path.dirname(__file__))
    
    is_git_repo = os.path.exists(os.path.join(package_root, ".git"))
    in_site_packages = "site-packages" in __file__
    
    return test_module is not None and is_git_repo and not in_site_packages

def parse_args():
    parser = argparse.ArgumentParser(
        description="A powerful yet easy-to-use todo TUI",
        prog="todoism"
    )
    parser.add_argument("-v", "--version",
        action="store_true",
        help="show version information")
    
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
    )
    
    add_parser = subparsers.add_parser("add", 
        help="add a new todo task (with options --flag/-f, see add --help)",
        description="Add a new todo task with optional flag")
    add_parser.add_argument("text", 
        type=str, 
        help="task description text (must be in quotes)"
        )
    add_parser.add_argument("-f", "--flag", 
        action="store_true", 
        help="mark the task as flagged")
    
    delete_parser = subparsers.add_parser("delete",
        help="delete a task by ID (see delete --help)",
        description="Delete a todo task by its ID")
    delete_parser.add_argument("id",
        type=int,
        help="task ID to delete")
    
    subparsers.add_parser("list",
        help="list all todos",
        description="Display all todo tasks in CLI mode")

    if is_dev_environment():
        parser.add_argument("--dev",
            action="store_true",
            help="run in development mode (with profiling)")
        parser.add_argument("--profile",
            action="store_true",
            help="enable profiling for performance analysis")
    
    return parser.parse_args()

def validate_text(text):
    if not text or not text.strip():
        raise argparse.ArgumentTypeError("Todo text cannot be empty")
    return text.strip()
    
def run():
    args = parse_args()
    
    if args.version:
        pr.print_version()
    elif args.command == "add":
        validated_text = validate_text(args.text)
        tsk.add_new_task_cli(validated_text, args.flag)
    elif args.command == "delete":
        tsk.delete_task_cli(args.id)
    elif args.command == "list":
        todos = tsk.load_tasks()
        pr.print_tasks_cli(todos)
    else:
        if hasattr(args, "dev") and args.dev:
            if is_dev_environment():
                import todoism.state as st
                st.dev_mode = True
        if hasattr(args, "profile") and args.profile:
            if is_dev_environment():
                import cProfile
                import pstats
    
                profile_file = "todoism_profile.prof"
                profiler = cProfile.Profile()
                profiler.enable()
    
                curses.wrapper(main.main)
    
                profiler.disable()
                profiler.dump_stats(profile_file)
    
                p = pstats.Stats(profile_file)
                p.sort_stats('cumulative').print_stats(30)
                print(f"\nProfile data saved to: {profile_file}")
                return
            else:
                print("Profile mode not available in PyPi Installation!")
        else:
            curses.wrapper(main.main)
