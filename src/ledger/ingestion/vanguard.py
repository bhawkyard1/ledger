from calendar import monthrange
from datetime import date

from ledger.ingestion import Ingestor
from ledger.transaction import Transaction, TransactionType


class Vanguard(Ingestor):
    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    def _get_last_day(self, year, month):
        return monthrange(year, month)[-1]

    def ingest(self):
        transactions = []
        for idx, line in enumerate(reversed(self.data[2:])):
            print(repr(line))
            midx = idx * 3
            datestr, begin, pay_in_out, market_change, income, fees, personal_returns, cumulative_returns, end = [x for x in line.split("\t") if x]
            month, year = datestr.split(" ")
            start_month = date(int(year), self.months[month], 1)
            end_month = date(
                int(year),
                self.months[month],
                self._get_last_day(int(year), self.months[month])
            )
            pay_in_out = self.to_pence(pay_in_out)
            print(f"market change raw {market_change}")
            market_change = self.to_pence(market_change)
            fees = self.to_pence(fees)
            starting_balance = self.to_pence(begin)
            ending_balance = self.to_pence(end)
            transactions += ([
                Transaction(
                    idx=midx,
                    date=start_month,
                    account="VANGUARD",
                    ttype=TransactionType.DIRECT_DEBIT,
                    description="VANGUARD_LINKED_ACCOUNT",
                    amount=pay_in_out,
                    balance=starting_balance + pay_in_out
                ),
                Transaction(
                    idx=midx+1,
                    date=end_month,
                    account="VANGUARD",
                    ttype=TransactionType.INTEREST,
                    description="THE_MARKETS",
                    amount=market_change,
                    balance=starting_balance + pay_in_out + market_change
                ),
                Transaction(
                    idx=midx+2,
                    date=end_month,
                    account="VANGUARD",
                    ttype=TransactionType.BANK_PAYMENT,
                    description="FEES",
                    amount=fees,
                    balance=ending_balance
                )
            ])
        return transactions

    @property
    def suitable(self) -> bool:
        return self.data[0].startswith("VANGUARD")

    def to_pence(self, figure: str) -> int:
        # Clip £
        negative = False
        for i, c in enumerate(figure):
            if c == "\u2212":
                negative = True
            elif c.isdigit():
                break
        figure = figure[i:].replace(",", "")
        pounds, pence = figure.split(".")

        val = int(pounds) * 100 + int(pence)
        if negative:
            val = -val
        print(f"figure {figure} -> {val}")
        return val