import os

def envvar(key, default=None):
    return os.environ.get(key, default)
