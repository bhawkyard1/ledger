from datetime import date

from ledger.ingestion import Ingestor
from ledger.transaction import Transaction, TransactionType


class Skipton(Ingestor):
    def ingest(self):
        transactions = []
        for idx, line in enumerate(reversed(self.data[1:])):
            print(repr(line),[x for x in line.split("\t") if x])
            datestr, desc, pay_in, pay_out, balance = [x for x in line.split("\t") if x]
            day, month, year = datestr.split("/")
            amount = self.to_pence(pay_in) if pay_in else -self.to_pence(pay_out)
            balance = self.to_pence(balance)

            transactions.append(
                Transaction(
                    idx=idx,
                    date=date(year, month, day),
                    account="SKIPTON ONLINE",
                    ttype=TransactionType.DIRECT_DEBIT,
                    description="SKIPTON_LINKED_ACCOUNT",
                    amount=amount,
                    balance=balance
                )
            )
        return transactions

    @property
    def suitable(self) -> bool:
        return self.data[0].startswith("SKIPTON")

    def to_pence(self, figure: str) -> int:
        # Clip £
        figure = figure.replace("£", "")
        figure = figure.replace(",", "")
        pounds, pence = figure.split(".")
        val = int(pounds) * 100 + int(pence)
        return val