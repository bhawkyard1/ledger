from datetime import date

from ledger import reverse_enumerate
from ledger.ingestion import Ingestor
from ledger.transaction import Transaction, TransactionType


class LLoydsIngestor(Ingestor):
    """ Ingests a lloyds csv file. """
    transaction_type_mapping = {
        "DD": TransactionType.DIRECT_DEBIT,
        "FPI": TransactionType.BANK_TRANSFER,
        "DEP": TransactionType.BANK_PAYMENT,
        "PAY": TransactionType.BANK_PAYMENT,
        "SO": TransactionType.STANDING_ORDER,
        "DEB": TransactionType.DEBIT_CARD_PAYMENT,
        "BGC": TransactionType.WAGES,
        "FPO": TransactionType.BANK_TRANSFER,
        "": TransactionType.NULL
    }

    def _convert_decimal(self, val: str) -> int:
        """ Converts a decimal string to an int representing pennies. """
        spl = val.split(".")
        if len(spl) < 2:
            raise RuntimeError(f"Invalid value provided to convert: '{val}'!")
        total = int(spl[0] or "0") * 100
        if len(spl) > 1:
            total += int(spl[1])
        return total

    def ingest(self):
        super(LLoydsIngestor, self).ingest()
        transactions = []
        data = self.data
        if len(data) < 2:
            return
        data = data[1:]
        for idx, item in enumerate(reversed(data)):
            print(f"{idx}: {item}")
            strdate, ttype, sort, acct, actor, pay_out, pay_in, end = item.split(",")
            day, month, year = [int(x) for x in strdate.split("/")]
            dateobj = date(year, month, day)
            sort = sort[1:]

            if not pay_out:
                amount = self._convert_decimal(pay_in)
            else:
                amount = -self._convert_decimal(pay_out)

            transactions.append(
                Transaction(
                    idx=idx,
                    account=f"{acct}, {sort}",
                    date=dateobj,
                    ttype=self.transaction_type_mapping[ttype],
                    description=actor,
                    amount=amount,
                    balance=self._convert_decimal(end)
                )
            )
        # raise Exception
        return transactions

    @property
    def suitable(self) -> bool:
        return (
            self.data[0] ==
            "Transaction Date,Transaction Type,Sort Code,Account Number,Transaction Description,Debit Amount,Credit "
            "Amount,Balance"
        )