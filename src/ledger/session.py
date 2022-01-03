import json
import pathlib

from ledger.transaction import Transaction


class Session:
    def __init__(self):
        self._project = None
        self.configuration = {
            "accounts": {}
        }
        self.transactions = []

    @property
    def project(self) -> pathlib.Path:
        return pathlib.Path(self._project)

    @project.setter
    def project(self, value: str):
        self._project = value
        if self.project.is_file():
            with open(self._project) as f:
                data = json.load(f)
            self.transactions = [Transaction.from_dict(d) for d in data["transactions"]]
            self.configuration = data["configurations"]

    def save(self):
        data = {
            "configuration": self.configuration,
            "transactions": [t.to_dict() for t in self.transactions]
        }
        with open(self.project.expanduser().resolve(), "w+") as f:
            f.write(json.dumps(data, indent=4, sort_keys=True))
