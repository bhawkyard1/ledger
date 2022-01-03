import hashlib
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from ledger import classproperty

class Serializable(ABC):
    def __init__(self, *args, **kwargs):
        super(Serializable, self).__init__(*args, **kwargs)

    @classmethod
    def batch_delete(cls, items):
        if not items:
            return

        typ = type(items[0])
        for item in items:
            if not isinstance(item, typ):
                raise RuntimeError(
                    f"Can only batch serialize instances of the same class, or children. First item provided was type {typ}"
                    f"but this is type {type(item)}!"
                )

        con = sqlite3.connect(cls.db_path)
        cur = con.cursor()
        contents = cls.table_contents

        cmd = f"CREATE TABLE IF NOT EXISTS {cls.table_name} (uid text, {contents}, PRIMARY KEY(uid))"
        print(cmd)
        cur.execute(cmd)

        conditions = " OR ".join(f"uid=\"{x.uid}\"" for x in items)
        cmd = f"DELETE FROM {cls.table_name} WHERE ({conditions})"

        cur.execute(cmd)

        con.commit()
        con.close()

    @classmethod
    def batch_serialize(cls, items):
        if not items:
            return

        typ = type(items[0])
        for item in items:
            if not isinstance(item, typ):
                raise RuntimeError(
                    f"Can only batch serialize instances of the same class, or children. First item provided was type {typ}"
                    f"but this is type {type(item)}!"
                )

        con = sqlite3.connect(cls.db_path)
        cur = con.cursor()
        contents = cls.table_contents

        cmd = f"CREATE TABLE IF NOT EXISTS {cls.table_name} (uid text, {contents}, PRIMARY KEY(uid))"
        print(cmd)
        cur.execute(cmd)

        question_marks = f"({cls._question_marks(contents.count(',') + 1)})"
        cmd = f"INSERT OR REPLACE INTO {cls.table_name} VALUES {question_marks}"

        values = []
        for item in items:
            values.append([str(x) for x in (item.uid,) + item.tuple])
        valuestr = f"({'), ('.join(', '.join(v) for v in values)})"

        print(f"{cmd}, {valuestr}")
        cur.executemany(cmd, values)

        con.commit()
        con.close()

    @classproperty
    def db_path(cls):
        path = Path(".") / Path("ledger.db")
        if not path.is_file():
            raise RuntimeError(f"{path} does not exist! Please use ledger init to create this file.")
        return path

    def delete(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        contents = self.table_contents
        cmd = f"CREATE TABLE IF NOT EXISTS ? (uid text, ?, PRIMARY KEY(uid))", (self.table_name, contents)
        # print(cmd)
        cur.execute(*cmd)
        cmd = f"DELETE FROM ? WHERE (uid=?)", (self.table_name, self.uid)
        cur.execute(*cmd)
        con.commit()
        con.close()

    @classmethod
    def filter(cls, query):
        con = sqlite3.connect(cls.db_path)
        cur = con.cursor()
        if query:
            cmd = f"SELECT * FROM {cls.table_name} WHERE {query}"
        else:
            cmd = f"SELECT * FROM {cls.table_name}"
        items = []
        # print(cmd)
        for tup in cur.execute(cmd).fetchall():
            item = cls(*tup[1:])
            items.append(item)
        return items

    @property
    @abstractmethod
    def hash_data(self) -> tuple:
        """ Data used to hash this object. """
        return tuple()

    @classmethod
    def _question_marks(self, count):
        return ", ".join("?"*(count + 1))

    def serialize(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        contents = self.table_contents
        cmd = "CREATE TABLE IF NOT EXISTS ? (uid text, ?, PRIMARY KEY(uid))", (self.table_name, contents)
        # print(cmd)
        cur.execute(*cmd)
        cmd = f"INSERT OR UPDATE INTO {self.table_name} VALUES ({self._question_marks(contents.count(',') + 1)})"
        values = (self.uid,) + self.tuple
        # print(f"{cmd}, {values}")
        cur.execute(cmd, values)
        con.commit()
        con.close()

    @classproperty
    @abstractmethod
    def table_contents(cls):
        return ""

    @classproperty
    @abstractmethod
    def table_name(cls):
        return ""

    @property
    @abstractmethod
    def tuple(self):
        return tuple()

    @property
    def uid(self):
        # print(f"Compute hash for {self}")
        h = hashlib.md5()
        for x in self.hash_data:
            # print(f"\tupdating hash with {x}: {str(x).encode()}")
            h.update(str(x).encode())
        # print(f"hash is {h.hexdigest()}")
        return h.hexdigest()
