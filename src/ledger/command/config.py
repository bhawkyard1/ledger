import argparse
import json
import sys
from pathlib import Path

from ledger import classproperty
from ledger.command import Command
from ledger.config import get_config_data, remove_config_value, set_config_value

class Config(Command):
    names = ("config", "c")
    def __call__(self, args):
        args = self.parser.parse_args(args)
        if not args.add_or_remove:
            self._print_config()
        else:
            self._update_config(
                args.add_or_remove,
                args.values
            )

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Used to edit or view the ledger config json file.",
            prog=f"{sys.argv[0]} {self.names[0]}"
        )
        parser.add_argument("add_or_remove", type=str,
            help="+ if you want to add or change a value, - to remove. If neither is provided, the config is printed.",
            choices=("+", "-"),
            nargs="?",
            default=None
        )
        parser.add_argument("values", type=str, nargs="*",
            help=("One or more config operations. If you are adding a value you must specify the path, delimited by ':' "
                 "and then have an '=' before the value, e.g. foo:bar:baz=quux. If you want to remove an element a path"
                  "to it will suffice e.g. foo:bar:baz"
            )
        )
        return parser

    @property
    def path(self):
        return Path("./ledger_config.json")

    def _print_config(self):
        print(
            json.dumps(
                get_config_data(),
                indent=4,
                sort_keys=True
            )
        )

    def _update_config(self, add_or_remove, values):
        if add_or_remove == "+":
            for arg in values:
                print(arg)
                path, value = arg.split("=", 1)
                frags = path.split(":")
                set_config_value(frags, value)
        elif add_or_remove == "-":
            for arg in values:
                remove_config_value(arg.split(":"))
        else:
            raise RuntimeError(f"First argument must be '+' or '-' but here it is '{add_or_remove}'!")

