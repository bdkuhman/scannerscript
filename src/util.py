import os

def envvar(key, default=None):
    return os.environ.get(key, default)

def mapGet(map, key):
    try:
        return map[key]
    except KeyError:
        print(f"{key} is not a valid key")
        return None