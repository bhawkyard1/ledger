from datetime import date

from ledger.ingestion import Ingestor
from ledger.transaction import Transaction, TransactionType


class LLoydsCreditIngestor(Ingestor):
    """ Ingests csv statements for lloyds credit cards. """
    def _convert_decimal(self, val: str) -> int:
        """ Converts a decimal string to an int representing pennies. """
        spl = val.split(".")
        total = int(spl[0] or "0") * 100
        if len(spl) > 1:
            if len(spl[1]) == 1:
                spl[1] += "0"
            total += int(spl[1])
        return total

    def ingest(self):
        super(LLoydsCreditIngestor, self).ingest()
        transactions = []
        data = self.data
        if len(data) < 2:
            return
        data = data[1:]
        balance = 0
        for idx, item in enumerate(reversed(data)):
            print(f"{idx}: {item} -> {item.split(',')}")
            strdate, _, __, description, pay_out, ___ = item.split(",")
            day, month, year = [int(x) for x in strdate.split("/")]
            dateobj = date(year, month, day)

            amount = -self._convert_decimal(pay_out)
            balance += amount

            transactions.append(
                Transaction(
                    idx=idx,
                    account=f"LLOYDS_CREDIT",
                    date=dateobj,
                    ttype=TransactionType.CREDIT_CARD_PAYMENT,
                    description=description,
                    amount=amount,
                    balance=balance
                )
            )
        # raise Exception
        return transactions

    @property
    def suitable(self) -> bool:
        return self.data[0].startswith(
            "Date,Date entered,Reference,Description,Amount,"
        )