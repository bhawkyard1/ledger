import argparse
import sys

from ledger import classproperty
from ledger.command import Command
from ledger.command.output import chunks
from ledger.transaction import Transaction

class Delete(Command):
    names = ("delete", "del")
    def __call__(self, args):
        args = self.parser.parse_args(args)
        if not args.transaction_ids and not sys.stdin.isatty():
            args.transaction_ids = [l.rstrip() for l in sys.stdin.read().split(" ")]

        deleted = []
        for chunk in chunks(args.transaction_ids, 100):
            transactions = Transaction.filter(
                " OR ".join(f"uid=\"{uid}\"" for uid in chunk or [""])
            )
            Transaction.batch_delete(transactions)
            deleted += transactions

        print("Removed the following transactions:")
        for t in deleted:
            print(t)

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Deletes transactions from the ledger given a space separated list of transaction IDs.",
            prog=f"{sys.argv[0]} {self.names[0]}"
        )
        parser.add_argument(
            "transaction_ids",
            type=str,
            help="The IDs of the transactions to delete.",
            nargs="*"
        )
        return parser