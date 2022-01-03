import argparse
import datetime
import sys
from collections import defaultdict
from datetime import date

from ledger import pence_to_pounds, daterange, classproperty, get_date_from_string
from ledger.command import Command
from ledger.transaction import Transaction


class Balance(Command):
    names = ("balance", "b")
    def __call__(self, args):
        args = self.parser.parse_args(args)
        if not args.end_date:
            if args.start_date:
                date = get_date_from_string(args.start_date)
            else:
                date = self._get_todays_date()
            self._get_balance_on_date(date)
        elif args.start_date and args.end_date:
            start = get_date_from_string(args.start_date)
            end = get_date_from_string(args.end_date)
            self._get_balance_between_dates(start, end, args.delta_amount, args.delta_unit)

    def get_relevant_transactions_for_date(self, date):
        transactions = Transaction.filter(f"date<\"{date}\"")
        by_account = defaultdict(list)
        for t in transactions:
            by_account[t.account].append(t)
        best = []
        for trs in by_account.values():
            srt = list(sorted(trs, key=lambda x: (x.date, x.idx)))
            best.append(srt[-1])
        return best

    def _get_balance_between_dates(self, start, end, delta_amount=1, delta_unit="days"):
        if delta_unit == "months":
            delta = (delta_amount, delta_unit)
        else:
            print(f"{delta_unit} {delta_amount}")
            delta = datetime.timedelta(**{delta_unit: delta_amount})

        for x in daterange(start, end, delta):
            relevant = self.get_relevant_transactions_for_date(x)
            total = sum(t.balance for t in relevant)
            print(f"{x} {pence_to_pounds(total)}")

    def _get_balance_on_date(self, date):
        best = self.get_relevant_transactions_for_date(date)
        print(f"Balance as of {date}:")
        for t in best:
            print(f"\t{t.nice_account_name}: {pence_to_pounds(t.balance)}")
        total = sum(t.balance for t in best)
        print(f"TOTAL: {pence_to_pounds(total)}")

    def _get_todays_date(self):
        return date.today()

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Used to show the balance in all accounts on a specific date, or between two dates.",
            prog=f"{sys.argv[0]} {self.names[0]}"
        )
        parser.add_argument("start_date", type=str, nargs="?",
            help=(
                "The start date for the balance calculation. If no end date is provided, calculate for this date only. "
                "If no start date is provided, use the current date."
            )
        )
        parser.add_argument("end_date", type=str, nargs="?",
            help="The end date for the balance calculation. Optional."
        )
        parser.add_argument("--delta-amount", type=int,
            help=("If we're stepping between two dates and printing the balance we can provide an amount and a unit "
                 "of time to step."),
            nargs=1,
            default=1
        )
        parser.add_argument("--delta-unit", type=str, choices=[
                "years", "months", "weeks", "days"
            ],
            default="months"
        )
        return parser