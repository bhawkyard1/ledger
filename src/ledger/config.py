import json
from pathlib import Path

def _check_and_create():
    if not get_config_path().is_file():
        with open(get_config_path(), "w+") as f:
            f.write("{}")

def get_config_path():
    return Path("./ledger_config.json")

def get_config_data():
    _check_and_create()
    with open(get_config_path()) as f:
        data = json.load(f)
    return data

def get_config_value(path, default=None):
    data = get_config_data()
    for frag in path:
        if frag not in data:
            return default
        data = data[frag]
    return data

def remove_config_value(path):
    data = cur = get_config_data()
    for frag in path[:-1]:
        print(f"{cur} get {frag}")
        if frag not in cur:
            return
        cur = cur[frag]
    print(f"{cur}, del, {path[-1]}")
    del cur[path[-1]]
    with open(get_config_path(), "w") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))

def set_config_value(path, value):
    data = cur = get_config_data()
    for frag in path[:-1]:
        if frag not in cur:
            cur[frag] = {}
        cur = cur[frag]

    cur[path[-1]] = value
    with open(get_config_path(), "w") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))