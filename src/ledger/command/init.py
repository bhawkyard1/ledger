import argparse
import sqlite3
import sys
from pathlib import Path

from ledger import classproperty
from ledger.command import Command


class Init(Command):
    names = ("init", "ini")
    def __call__(self, args):
        args = self.parser.parse_args

        path = Path(".") / Path("ledger.db")
        con = sqlite3.connect(path)
        con.commit()

        print(f"Initialised ledger at {path}.")

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Used to initalise a new ledger project in the current directory.",
            prog=f"{sys.argv[0]} {self.names[0]}"
        )
        return parser
