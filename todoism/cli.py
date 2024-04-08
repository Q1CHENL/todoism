import argparse
import re

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add", metavar="TEXT", type=validate_text, help="add new todo")
    parser.add_argument("-d", "--delete", metavar="ID", type=validate_id, help="delete todo by id")
    parser.add_argument("-p", "--print-all", action="store_true", help="print all todos")
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
