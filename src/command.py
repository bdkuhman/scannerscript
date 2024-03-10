from mode import *
import re

def handle_command(input):
    global scannermode

    print(f"COMMAND: {input}")

    mode = re.match(MODE_REGEX, input)
    if mode:
        scannermode = Mode.value(mode.group(1))
        print(f"SET scannermode to {scannermode}")
        return