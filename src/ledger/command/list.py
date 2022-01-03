import argparse
import sys

from ledger import classproperty, get_date_from_string
from ledger.command import Command
from ledger.config import get_config_value
from ledger.transaction import Transaction


class List(Command):
    names = ("list", "ls")
    def __call__(self, args):
        args = self.parser.parse_args(args)

        extras = []
        if args.start_date:
            extras.append(f"date>=\"{get_date_from_string(args.start_date)}\"")
        if args.end_date:
            extras.append(f"date<\"{get_date_from_string(args.end_date)}\"")

        parameters = " ".join(args.parameters)
        for key, value in get_config_value(["account_names"], {}).items():
            parameters = parameters.replace(value, key)

        if parameters:
            if extras:
                parameters = f"({parameters}) AND {' AND '.join(extras)}"
        else:
            parameters = ' AND '.join(extras)

        transactions = []
        for t in sorted(Transaction.filter(parameters), key=lambda x: (x.date, x.idx)):
            transactions.append(t)
        print(" ".join(str(t.uid) for t in transactions))

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Lists the IDs of the transactions matching the supplied parameters.",
            prog=f"{sys.argv[0]} {self.names[0]}"
        )
        parser.add_argument("parameters", type=str, nargs="*")
        parser.add_argument("--start-date", "-sd", type=str, help="Date to start searching (inclusive).")
        parser.add_argument("--end-date", "-ed", type=str, help="Date to stop searching (non-inclusive).")
        return parser

