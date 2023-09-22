import re
from datetime import date

from ledger.ingestion import Ingestor
from ledger.transaction import Transaction, TransactionType


class PremiumBondsIngestor(Ingestor):
    def ingest(self):
        transactions = []
        i = 1
        cnt = 0
        while i < len(self.data):
            line = self.data[i]

            if line == "Transaction details":
                date_str, type = self.data[i + 1].split("\t")
                amount = self._pounds_to_pence(self.data[i + 2])
                balance = self._pounds_to_pence(self.data[i + 3])

                day, month, year = [int(x) for x in date_str.split("/")]
                dateobj = date(year, month, day)

                ttype = {
                    "Auto prize reinvestment": TransactionType.INTEREST,
                    "Debit card online deposit": TransactionType.DIRECT_DEBIT,
                    "BACS payment": TransactionType.BANK_PAYMENT,
                    "Faster Payment deposit": TransactionType.BANK_PAYMENT
                }[type.strip()]

                transactions.append(
                    Transaction(
                        idx=cnt,
                        date=dateobj,
                        account="PREMIUM_BONDS",
                        ttype=ttype,
                        description="PREMIUM_BONDS_LINKED_ACCOUNT",
                        amount=(
                            -amount if ttype == TransactionType.BANK_PAYMENT
                            else amount
                        ),
                        balance=balance
                    )
                )
                cnt += 1

                i += 3
            else:
                i += 1

        for t in transactions:
            print(t)
        return transactions

    def _pounds_to_pence(self, figure):
        for i, c in enumerate(figure):
            if c.isdigit():
                break
        figure = figure[i:].replace(",", "")
        if "." in figure:
            pounds, pence = figure.split(".")
        else:
            pounds, pence = figure, "0"
        return int(pounds) * 100 + int(pence)

    @property
    def suitable(self) -> bool:
        return self.data[0].startswith("PREMIUM_BONDS")