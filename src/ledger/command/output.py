import argparse
import sys

from ledger import classproperty, pence_to_pounds, print_columns, TextColor
from ledger.command import Command
from ledger.config import get_config_value
from ledger.transaction import Transaction

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class Output(Command):
    names = ("output", "o")
    def __call__(self, args):
        args = self.parser.parse_args(args)
        if not args.transaction_ids and not sys.stdin.isatty():
            args.transaction_ids = [l.rstrip() for l in sys.stdin.read().split(" ")]

        cols = [s for s in args.format_str.split(" ")]
        transactions = []
        for chunk in chunks(args.transaction_ids, 100):
            transactions += Transaction.filter(
                " OR ".join(f"uid=\"{uid}\"" for uid in chunk or [""])
            )
        data = []
        for t in sorted(transactions, key=lambda x: tuple(getattr(x, k) for k in args.sort_by)):
            nice_account = get_config_value(["account_names", t.account], t.account)
            nice_description = get_config_value(["account_names", t.description], t.description)
            format_dict = {
                "date": t.date,
                "input": nice_account if t.amount < 0 else nice_description,
                "amount": pence_to_pounds(t.amount),
                "output": nice_description if t.amount < 0 else nice_account,
                "account": nice_account,
                "description": nice_description,
                "balance": pence_to_pounds(t.balance),
                "index": t.idx,
                "uid": t.uid,
                "raw": t.tuple
            }
            formatted = [TextColor.OKGREEN.value if t.amount >= 0 else TextColor.FAIL.value] + [s.format(**format_dict) for s in cols]
            data.append(formatted)

        if not data:
            return

        print_columns(data)

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Prints out a list of transactions given a space separated list of transaction IDs.",
            prog=f"{sys.argv[0]} {self.names[0]}"
        )
        parser.add_argument(
            "--format-str",
            "-fs",
            type=str,
            help="The string to use to format the output.",
            default="{date}: {input} -> {amount} -> {output} ({account} = {balance})",
            nargs="?"
        )
        parser.add_argument(
            "--sort-by",
            type=str,
            nargs="*",
            help="The properties to sort the output by.",
            default=["date", "idx"],
            choices=([
                "date",
                "idx",
                "amount"
            ])
        )
        parser.add_argument(
            "transaction_ids",
            type=str,
            help="The IDs of the transactions to output.",
            nargs="*"
        )
        return parser