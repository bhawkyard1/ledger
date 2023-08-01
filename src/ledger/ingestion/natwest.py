import csv
from datetime import date

from ledger.ingestion import Ingestor
from ledger.transaction import Transaction, TransactionType


class NationwideIngestor(Ingestor):
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
    def _convert_currency(self, val: str) -> int:
        """ Converts a decimal string to an int representing pennies. """
        multiplier = 1

        if val[0] == "-":
            multiplier = -1
            val = val[1:]

        spl = val.split(".")
        if len(spl) == 2:
            pounds, pennies = spl
            if len(pennies) == 1:
                pennies += "0"
        elif len(spl) == 1:
            pounds, pennies = spl[0], "00"
        else:
            raise RuntimeError("Could not make sense of {}!".format(val))

        try:
            return multiplier * 100 * int(pounds) + int(pennies)
        except ValueError:
            raise ValueError(
                f"Could not convert currency for value {val}!"
            )

    def _convert_transaction_type(self, val: str) -> TransactionType:
        matches = {
            "POS": TransactionType.DEBIT_CARD_PAYMENT,
            "IBP": TransactionType.BANK_PAYMENT,
        }
        if val in matches:
            return matches[val]
        return TransactionType.NULL

    def ingest(self):
        super(NationwideIngestor, self).ingest()
        transactions = []

        for i, line in enumerate(self.data):
            if line.split()[0].isdigit():
                start_idx = i
                break
        else:
            start_idx = None

        if start_idx is None:
            return
        data = self.data[start_idx:]

        for idx, item in enumerate(csv.reader(data, delimiter=',',
                                              quotechar='"')):
            print(idx, item)
            strdate, ttype, desc, value, balance, acct_name, acct_number = item
            desc = ", ".join([frag.strip() for frag in desc.split(",")])
            if len(desc) > 24:
                desc = desc[:24]
            datespl = strdate.split(" ")
            day = int(datespl[0])
            month = self.months[datespl[1]]
            year = int(datespl[2])

            dateobj = date(year, month, day)
            amount = self._convert_currency(value)

            transactions.append(
                Transaction(
                    idx=idx,
                    account=acct_name,
                    date=dateobj,
                    ttype=self._convert_transaction_type(ttype),
                    description=desc,
                    amount=amount,
                    balance=self._convert_currency(balance)
                )
            )
        return transactions

    @property
    def suitable(self) -> bool:
        return self.data[0].startswith("NATWEST")
