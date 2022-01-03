import argparse
import sys
from pathlib import Path

from ledger import classproperty
from ledger.command import Command
from ledger.ingestion import Ingestor
from ledger.transaction import Transaction


class Ingest(Command):
    names = ("ingest", "ing")

    def __call__(self, args):
        args = self.parser.parse_args(args)
        transactions = []
        if not args.files:
            raise RuntimeError("ingest command requires one or more paths!")
        for path in args.files:
            path = Path(path)
            if not path.expanduser().resolve().is_file():
                raise RuntimeError(f"{path} is not a valid file!")

            for cls in Ingestor.allSubclasses():
                inst = cls(path)
                if inst.suitable:
                    transactions += inst.ingest()
                    break
            else:
                raise RuntimeError(f"Could not find a suitable class to ingest {path}!")

        Transaction.batch_serialize(transactions)
        # for t in transactions:
        #     t.serialize()
        # transactions[0].serialize()
        # serialized = Transaction.filter("")
        # print(transactions[0].hash_data)
        # print(serialized[0].hash_data)

        print(f"Ingested: {', '.join(args.files)}")

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Used to ingest data from external sources (typically csv files) into the ledger database.",
            prog=f"{sys.argv[0]} {self.names[0]}"
        )
        parser.add_argument("files", nargs="*", help="The paths to the files you want to ingest.")
        return parser

from ledger.ingestion import amex
from ledger.ingestion import lloyds
from ledger.ingestion import nationwide
from ledger.ingestion import premium_bonds
from ledger.ingestion import vanguard
