import traceback

from ledger.command import Command
from ledger.session import Session


def get_command_class(command):
    for cls in Command.allSubclasses():
        inst = cls()
        if inst.match(command):
            return inst

def run():
    command = input("> ")
    session = Session()
    while command not in ("q", "quit", "exit"):
        command_class = get_command_class(command)
        if command_class:
            try:
                result = command_class(command, session)
                print(result)
            except Exception:
                traceback.print_exc()
        else:
            print(f"Error! Unrecognised command '{command}'!")

        command = input("> ")