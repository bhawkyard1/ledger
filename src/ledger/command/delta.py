import argparse
import sys
from collections import defaultdict

from ledger import pence_to_pounds, classproperty
from ledger.command import Command
from ledger.transaction import Transaction


class Delta(Command):
    names = ("delta", "d")
    def __call__(self, args):
        args = self.parser.parse_args(args)
        transactions = Transaction.filter(f"date>=\"{args.start_date}\" AND date<\"{args.end_date}\"")
        accounts = {}
        in_by_account = defaultdict(int)
        out_by_account = defaultdict(int)
        for t in transactions:
            if t.is_internal and args.ignore_internal:
                print(f"Skipping internal transaction {t}")
                continue

            accounts[t.account] = t.nice_account_name
            if t.amount > 0:
                in_by_account[t.account] += t.amount
            else:
                out_by_account[t.account] -= t.amount

        for account, name in sorted(accounts.items()):
            inp = in_by_account[account]
            outp = out_by_account[account]
            diff = inp - outp
            print(f"{name}:\n\tIn: {pence_to_pounds(inp)}\n\tOut: {pence_to_pounds(outp)}\n\tDifference: {pence_to_pounds(diff)}\n")

        total_in = sum(in_by_account.values())
        total_out = sum(out_by_account.values())
        diff = total_in - total_out
        print(f"TOTAL:\n\tIn: {pence_to_pounds(total_in)}\n\tOut: {pence_to_pounds(total_out)}\n\tDifference: {pence_to_pounds(diff)}")

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Used to show the amount of money that has entered and left the recorded accounts.",
            prog=f"{sys.argv[0]} {self.names[0]}"
        )
        parser.add_argument("start_date", type=str, help="The date to start from, formatted {yyyy}-{mm}-{dd}.")
        parser.add_argument("end_date", type=str, help="The date to end at non inclusive, formatted {yyyy}-{mm}-{dd}.")
        parser.add_argument("--ignore-internal", "-ii", action="store_true",
            help="Whether to ignore transactions which have moved money between internal accounts."
        )
        return parser
