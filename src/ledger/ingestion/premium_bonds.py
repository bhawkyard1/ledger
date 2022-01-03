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
            spl = [x for x in line.split("\t") if x]
            print(spl)
            if len(spl) != 4:
                i += 1
                continue

            if re.match("[0-9]{2}/[0-9]{2}/[0-9]{2}", spl[0]):
                day, month, year = [int(x) for x in spl[0].split("/")]
                dateobj = date(year, month, day)
                amount = self._pounds_to_pence(spl[2])
                balance = self._pounds_to_pence(spl[3])

                transactions.append(
                    Transaction(
                        idx=cnt,
                        date=dateobj,
                        account="PREMIUM_BONDS",
                        ttype=TransactionType.ONLINE_DEBIT_CARD_PAYMENT,
                        description="PREMIUM_BONDS_LINKED_ACCOUNT",
                        amount=amount,
                        balance=balance
                    )
                )
                cnt += 1
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