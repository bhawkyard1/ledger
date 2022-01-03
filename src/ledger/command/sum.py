import argparse
import sys

from ledger import classproperty, pence_to_pounds, remove_colors
from ledger.command import Command


class Sum(Command):
    names = "sum", "s"
    def __call__(self, args):
        args = self.parser.parse_args(args)
        if not args.values and not sys.stdin.isatty():
            args.values = [remove_colors(l.strip().replace(" ", "")) for l in sys.stdin]

        total = 0
        for value in args.values:
            total += self._get_pence_from_value(value)
        print(pence_to_pounds(total))

    def _get_pence_from_value(self, value):
        if all(c.isdigit() for c in value): # Pure number (assume pence)
            return int(value)
        elif value.startswith("£"):
            spl = value[1:].split(".")
            if len(spl) == 2:
                return 100 * int(spl[0]) + int(spl[1])
            elif len(spl) == 1:
                return 100 * int(spl[0])
        elif value.startswith("-"):
            return -self._get_pence_from_value(value[1:])
        raise RuntimeError(f"Could not get a value from '{value}'!")

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Adds numbers together."
        )
        parser.add_argument("values", nargs="*", help="The values to add up.")
        return parser