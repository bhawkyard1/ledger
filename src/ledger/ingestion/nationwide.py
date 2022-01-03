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
        if val[0].isdigit():
            raise RuntimeError(f"Unexpected value {val}, must start with '£'!")
        val = val[1:]
        pounds, pennies = val.split(".")
        return 100 * int(pounds) + int(pennies)

    def _convert_transaction_type(self, val: str) -> TransactionType:
        matches = {
            "Forwarded Credit Switch Balance": TransactionType.BANK_PAYMENT,
            "Transfer from Switching Offer": TransactionType.BANK_TRANSFER,
            "Visa purchase": TransactionType.DEBIT_CARD_PAYMENT,
            "Contactless Payment": TransactionType.DEBIT_CARD_PAYMENT
        }
        if val in matches:
            return matches[val]

        if val.startswith("Direct debit "):
            return TransactionType.DIRECT_DEBIT
        elif val.startswith("ATM Withdrawal "):
            return TransactionType.ATM_WITHDRAWAL
        return TransactionType.NULL

    def ingest(self):
        super(NationwideIngestor, self).ingest()
        transactions = []
        data = self.data
        account = data[0].split(",")[1]
        if len(data) < 5: # Data starts on line 6
            return
        data = data[5:]
        print(f"data is {data}")

        for idx, item in enumerate(data):
            strdate, ttype, desc, pay_out, pay_in, balance = [f.strip('"') for f in item.split(",")]
            datespl = strdate.split(" ")
            print(f"datespl {datespl}")
            day = int(datespl[0])
            month = self.months[datespl[1]]
            year = int(datespl[2])

            dateobj = date(year, month, day)

            if not pay_out:
                amount = self._convert_currency(pay_in)
            else:
                amount = -self._convert_currency(pay_out)

            transactions.append(
                Transaction(
                    idx=idx,
                    account=account,
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
        return self.data[0].startswith("\"Account Name:\",\"FlexDirect Account")