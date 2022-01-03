import pathlib
from ledger import Discoverable


class Ingestor(Discoverable):
    def __init__(self, path: pathlib.Path):
        self.path = path
        self._data = None

    @property
    def data(self):
        if not self._data:
            with open(self.path, errors="replace") as f:
                self._data = [l.rstrip() for l in f.readlines()]
        return self._data

    def ingest(self):
        print(f"Ingesting {self.path} using {self.__class__}")

    @property
    def suitable(self) -> bool:
        return False
