from util import envvar
from enum import Enum

import time

MODE_REGEX = envvar("MODE_REGEX", r"^_CMD:MODE=(.*)$")

class Mode(Enum):
    IDLE = 0

scannermode = Mode.IDLE
lastscan = time.time()  # script load
def reset_mode():
    global scannermode
    global lastscan

    now = time.time()
    diff = now - lastscan

    print(f"Last scan {diff}s ago")

    if (now - lastscan) >= 180:  # 3 minutes
        print("resetting scan mode")
        scannermode = Mode.IDLE
    lastscan = now