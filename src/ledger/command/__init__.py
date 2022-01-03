import argparse
from abc import abstractmethod
from ledger import Discoverable, classproperty

class Command(Discoverable):
    names = tuple()

    @abstractmethod
    def __call__(self, command):
        pass

    def match(self, command):
        spl = command.split(" ")
        return spl[0] in self.names

    @classproperty
    def parser(self):
        return argparse.ArgumentParser()

    @classproperty
    def help(self):
        return self.parser.format_help()

from ledger.command.balance import Balance
from ledger.command.config import Config
from ledger.command.delete import Delete
from ledger.command.delta import Delta
from ledger.command.get_spending import GetSpending
from ledger.command.ingest import Ingest
from ledger.command.init import Init
from ledger.command.list import List
from ledger.command.output import Output
from ledger.command.sum import Sum