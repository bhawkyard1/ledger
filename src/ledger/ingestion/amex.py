from datetime import date

from ledger import reverse_enumerate
from ledger.ingestion import Ingestor
from ledger.transaction import Transaction, TransactionType

class AmexIngestor(Ingestor):
    @property
    def data(self):
        d = super(AmexIngestor, self).data
        return [d[0]] + list(reversed(d[1:]))

    def _find_last_balance(self, data):
        """ I pay off the credit card on the ~27th each month, paying off the balance for the period
            starting the previous month on the 14th and ending on the current month on the 13th.

            In other words, the most recent pay-off of the credit card represents the balance at the
            transaction before, and closest to, the 13th of the current month. We can then extrapolate
            this out on both sides to find the balance of all transactions.
        """
        for i, v in reverse_enumerate(data):
            formatted = self._get_data_from_line(v)
            if formatted["description"] == "AMEX_LINKED_ACCOUNT":
                last_payment_index, last_payment_date, last_payment_amount = i, formatted["date"], formatted["amount"]
                break
        else:
            raise RuntimeError("Could not find a record of any credit payment to the account, so unable to compute balance!")

        target_date = date(last_payment_date.year, last_payment_date.month, 13)
        for i, v in reverse_enumerate(data[:last_payment_index]):
            formatted = self._get_data_from_line(v)
            if formatted["date"] <= target_date:
                balance_index = i
                amount_to_arrive_at_balance = formatted["amount"]
                break
        else:
            raise RuntimeError(f"Could not find transaction on or before {target_date}!")

        return balance_index, amount_to_arrive_at_balance, -last_payment_amount

    def _get_data_from_line(self, line):
        data = {}
        spl = line.split(",")

        datestr = spl[0]
        amount = spl[-1]
        description = ",".join(spl[1:-1])
        day, month, year = [int(x) for x in datestr.split("/")]

        data["date"] = date(year, month, day)
        description = description.strip('"')
        while "  " in description:
            description = description.replace("  ", " ")
        data["amount"] = -int(amount.replace(".", ""))
        data["account"] = "AMEX"
        if description == "PAYMENT RECEIVED - THANK YOU":
            description = "AMEX_LINKED_ACCOUNT"
        data["description"] = description
        return data

    def ingest(self):
        super(AmexIngestor, self).ingest()
        transactions = []
        last_index, last_amount, last_balance = self._find_last_balance(self.data)
        print(f"at {last_index}, spent {last_amount} to reach a balance of {last_balance}")
        cur_index = last_index
        cur_amount = last_amount
        cur_balance = last_balance
        print(f"cur balance is {cur_balance}")
        # Extrapolate backwards
        while cur_index > 0:
            print(f"{cur_index}: {self.data[cur_index]}")
            line_data = self._get_data_from_line(self.data[cur_index])
            t=Transaction(
                idx=cur_index,
                date=line_data["date"],
                account=line_data["account"],
                ttype=TransactionType.CREDIT_CARD_PAYMENT,
                description=line_data["description"],
                amount=line_data["amount"],
                balance=cur_balance
            )
            transactions.append(t)
            # print(f"added transaction {t} bal {t.balance}")
            # raise Exception
            cur_amount = line_data["amount"]
            cur_balance -= cur_amount
            cur_index -= 1
        # raise Exception

        cur_index = last_index + 1
        cur_balance = last_balance
        # Extrapolate forwards
        while cur_index < len(self.data):
            line_data = self._get_data_from_line(self.data[cur_index])
            cur_balance += line_data["amount"]
            transactions.append(
                Transaction(
                    idx=cur_index,
                    date=line_data["date"],
                    account=line_data["account"],
                    ttype=TransactionType.CREDIT_CARD_PAYMENT,
                    description=line_data["description"],
                    amount=line_data["amount"],
                    balance=cur_balance
                )
            )
            cur_index += 1

        return list(sorted(transactions, key=lambda x: (x.date, x.idx)))

    @property
    def suitable(self) -> bool:
        return self.data[0] == "Date,Description,Amount"