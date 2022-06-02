import argparse
import calendar
import datetime
from collections import defaultdict
from datetime import date

from ledger import get_date_from_string, pence_to_pounds, classproperty, print_columns, daterange, date_subtract_delta, TextColor
from ledger.command import Command
from ledger.config import get_config_value
from ledger.transaction import Transaction


class GetSpending(Command):
    names = "get-spending", "gs"
    def __call__(self, args):
        args = self.parser.parse_args(args)

        if args.start_date:
            start_date = get_date_from_string(args.start_date, default_to_start=False)
        else:
            start_date = self._get_last_day_in_month(date.today())

        if args.end_date:
            end_date = get_date_from_string(args.end_date, default_to_start=False)
        else:
            cur = start_date
            start_date = datetime.date(cur.year, cur.month, 1)
            end_date = cur

        if args.mode == "all":
            self._get_spending(start_date, end_date, args.print_accounts, args.print_details)
        else:
            delta = {
                "daily": datetime.timedelta(days=1),
                "weekly": datetime.timedelta(weeks=1),
                "monthly": (1, "months"),
                "yearly": (1, "years")
            }[args.mode]
            for b in daterange(start_date, end_date, delta):
                a = date_subtract_delta(b, delta)
                self._get_spending(a, b, args.print_accounts, args.print_details)

    def _get_last_day_in_month(self, orig_date):
        """ Given a date return it, with the last day in the current month. """
        last_day = calendar.monthrange(orig_date.year, orig_date.month)[1]
        return date(orig_date.year, orig_date.month, last_day)

    def _get_spending(self, start, end, print_accounts=False, print_details=False):
        if start < end:
            relevant_transactions = Transaction.filter(
                f"date>=\"{start}\" AND date<\"{end}\""
            )
        else:
            relevant_transactions = Transaction.filter(
                f"date==\"{start}\""
            )
        spending_by_account = defaultdict(int)
        running_total = 0
        for t in sorted(relevant_transactions):
            if(
                t.amount < 0 and
                not t.is_internal and
                t.description not in get_config_value(["non_spending_outgoing_accounts"], [])
            ):
                running_total -= t.amount
                if print_details:
                    print(f"{TextColor.FAIL.value}ADDING:   {t} : {pence_to_pounds(running_total)}")
                spending_by_account[t.nice_account_name] -= t.amount
            elif t.description in get_config_value(["payback_descriptions"]):
                running_total -= t.amount
                if print_details:
                    print(f"{TextColor.OKGREEN.value}PAYBACK:  {t} : {pence_to_pounds(running_total)}")
                spending_by_account[t.nice_account_name] -= t.amount
            elif print_details:
                print(f"{TextColor.ENDC.value}IGNORING: {t} : {pence_to_pounds(running_total)}")

        data = []
        # print(spending_by_account)
        if print_accounts:
            for acct, spending in sorted(spending_by_account.items()):
                data.append(
                    [f"{acct}:", pence_to_pounds(spending)]
                )

        spending_total = sum(spending_by_account.values())
        data.append([
            f"{start} - {end} TOTAL:", pence_to_pounds(spending_total)
        ])

        print_columns(data)
        print("")

    @classproperty
    def parser(self):
        parser = argparse.ArgumentParser(
            description="Calculates spending between two dates, using some nasty hacks to correct for household bills."
        )
        parser.add_argument("start_date", type=str, nargs="?")
        parser.add_argument("end_date", type=str, nargs="?")
        parser.add_argument("--print-accounts", "-pa", action="store_true", help="Print a breakdown of spending by account.")
        parser.add_argument("--print-details", "-pd", action="store_true", help="Print the details about what is ignored and what isn't.")
        parser.add_argument("--mode", type=str,
            choices=["all", "daily", "weekly", "monthly", "yearly"],
            default="all",
            help="The time spans to get the spending for."
        )
        return parser
