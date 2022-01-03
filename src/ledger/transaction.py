import datetime
from enum import Enum

from ledger import classproperty, pence_to_pounds
from ledger.config import get_config_value
from ledger.serializable import Serializable


class TransactionType(Enum):
    NULL = 0
    DIRECT_DEBIT = 1
    BANK_TRANSFER = 2
    BANK_PAYMENT = 3
    STANDING_ORDER = 5
    DEBIT_CARD_PAYMENT = 6
    ONLINE_DEBIT_CARD_PAYMENT = 7
    WAGES = 8
    ATM_WITHDRAWAL = 9
    CREDIT_CARD_PAYMENT = 10
    INTEREST = 11

class Transaction(Serializable):
    def __init__(
        self,
        idx,
        date,
        account,
        ttype,
        description,
        amount,
        balance
    ):
        """ Make a new transaction.

            Args:
                data (Date)
        """
        super(Transaction, self).__init__()
        self.idx = idx
        self.account = account
        if isinstance(date, str):
            year, month, day = [int(x) for x in date.split("-")]
            date = datetime.date(year, month, day)
        self.date = date
        self.ttype = TransactionType(ttype)
        self.description = description
        self.amount = amount
        self.balance = balance

    def __eq__(self, other):
        try:
            return (
                self.balance == other.balance and
                self.date == other.date and
                self.amount == other.amount and
                self.description == other.description and
                self.ttype == other.ttype and
                self.account == other.account
            )
        except AttributeError:
            return False

    def __lt__(self, other):
        try:
            return (self.date, self.idx, self.account) < (other.date, other.idx, other.account)
        except AttributeError:
            return False

    def __str__(self):
        abs_amount = abs(self.amount)
        if self.amount < 0:
            return f"{self.date}: {self.nice_account_name} -> {pence_to_pounds(abs_amount)} -> {self.nice_description} (={pence_to_pounds(self.balance)})"
        return f"{self.date}: {self.nice_description} -> {pence_to_pounds(abs_amount)} -> {self.nice_account_name} (={pence_to_pounds(self.balance)})"

    @property
    def hash_data(self):
        return tuple([self.date, self.account, self.ttype, self.description, self.amount, self.balance])

    @property
    def is_internal(self):
        """ Whether this transaction represents moving money between accounts. """
        owned_accounts = get_config_value(["account_names"], {}).keys()
        return self.account in owned_accounts and self.description in owned_accounts

    @property
    def nice_account_name(self):
        return get_config_value(["account_names", self.account], default=self.account)

    @property
    def nice_description(self):
        return get_config_value(["account_names", self.description], default=self.description)

    @classproperty
    def table_name(cls):
        return "transactions"

    @classproperty
    def table_contents(cls):
        return "idx int, date text, account text, type int, description text, amount int, balance int"

    @property
    def tuple(self):
        return self.idx, self.date, self.account, self.ttype.value, self.description, self.amount, self.balance
