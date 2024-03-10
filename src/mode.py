from util import envvar
from enum import Enum

import time

class Mode(Enum):
    IDLE = 0
    CMD = 1

class Context(Enum):
    BCB_QTY = 0


scannermode = Mode.IDLE
scannerctx = None


lastscan = time.time()  # script load

def check_timeout():
    global scannermode
    global lastscan

    now = time.time()
    diff = now - lastscan

    print(f"Last scan {diff}s ago")

    if (now - lastscan) >= 180:  # 3 minutes
        print("resetting scan mode")
        set_mode(Mode.IDLE)
    lastscan = now

def set_mode(mode):
    global scannermode
    scannermode = mode #TODO: exceptions
    print(f"Current scanner mode is {scannermode}")

def set_context(context):
    global scannerctx
    scannerctx = context
    print(f"Current mode context is {scannerctx}")

def get_mode():
    global scannermode
    return scannermode

def get_context():
    global scannerctx
    return scannerctx

def reset_context():
    set_context(None)

def reset_mode():
    set_mode(Mode.IDLE)

def reset():
    reset_mode()
    reset_context()