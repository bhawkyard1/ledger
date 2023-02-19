import calendar
import datetime
from abc import ABC

from enum import Enum


def add_months_to_date(old_date, months):
    new_year = old_date.year
    new_month = old_date.month
    new_day = old_date.day

    new_month += months
    while new_month > 12:
        new_month -= 12
        new_year += 1
    while new_month < 1:
        new_month += 12
        new_year -= 1

    monthrange = calendar.monthrange(new_year, new_month)
    if new_day > monthrange[1]:
        new_day = monthrange[1]

    return datetime.date(new_year, new_month, new_day)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class TextColor(Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def remove_colors(text):
    for color in TextColor:
        text = text.replace(color.value, "")
    return text

class classproperty:
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)

def date_add_delta(date: datetime.date, delta):
    if isinstance(delta, tuple) and delta[1] == "months":
        date = add_months_to_date(date, delta[0])
    elif isinstance(delta, tuple) and delta[1] == "years":
        date = datetime.date(date.year + delta[0], date.month, date.day)
    else:
        date += delta
    return date

def date_subtract_delta(date: datetime.date, delta):
    if isinstance(delta, tuple) and delta[1] == "months":
        date = add_months_to_date(date, -delta[0])
    elif isinstance(delta, tuple) and delta[1] == "years":
        date = datetime.date(date.year - delta[0], date.month, date.day)
    else:
        date -= delta
    return date

def daterange(start, end, delta=None):
    if start > end:
        raise RuntimeError(f"Start date {start} must be before end date {end}!")
    if not delta:
        delta = datetime.timedelta(days=1)
    while start <= end:
        yield start
        start = date_add_delta(start, delta)

def get_date_from_string(date_str, default_to_start=True):
    to_replace = ("/.")
    for char in to_replace:
        date_str = date_str.replace(char, "-")

    spl = [int(x) for x in date_str.split("-")]
    if spl[0] > 32:
        if len(spl) == 2:
            spl.append(1 if default_to_start else calendar.monthrange(spl[0], spl[1])[1])
        year, month, day = spl
    else:
        if len(spl) == 2:
            spl.insert(0, 1 if default_to_start else calendar.monthrange(spl[1], spl[0])[1])
        day, month, year = spl
    return datetime.date(year, month, day)

class Discoverable(ABC):
    def __init__(self):
        super(Discoverable, self).__init__()

    @classmethod
    def allSubclasses(cls):
        return list(set(
            cls.__subclasses__() + sum(
                (s.allSubclasses() for s in cls.__subclasses__()), []
            )
        ))

def pence_to_pounds(pence: int) -> str:
    pabs = abs(pence)
    negative = pence < 0
    pdiv = (pabs // 100)
    pmod = str(pabs % 100).zfill(2)
    return f"{'-' if negative else ''}£{pdiv}.{pmod}"

def print_columns(data):
    for col in range(len(data[0])):
        maxlen = 0
        for row in data:
            lencol = len(remove_colors(row[col])) + 1
            if lencol > maxlen:
                maxlen = lencol

        for row in data:
            diff = maxlen - len(remove_colors(row[col]))
            row[col] += " " * diff

    for row in data:
        print(" ".join(row))

def reverse_enumerate(iterable):
    i = len(iterable)
    while i:
        i -= 1
        yield i, iterable[i]