import mode
from mode import Mode

from util import envvar

import barcodebuddy as bcb
import re

MODE_REGEX = envvar("MODE_REGEX", r"^_CMD:MODE=(.*)$")
BCB_REGEX = envvar("BCB_REGEX", r"^_CMD:BCB=(.*)$")


def handle_command(input):
    global scannermode
    
    if mode.get_context() == mode.Context.BCB_QTY:
        bcb.handle_cmd(input)
        return

    print(f"COMMAND: {input}")

    mode_cmd = re.match(MODE_REGEX, input)
    if mode_cmd:
        mode.set_mode(Mode[mode_cmd.group(1)])
        return
    
    bcb_cmd = re.match(BCB_REGEX, input)
    
    if bcb_cmd:
        mode.set_mode(Mode.CMD)
        command = bcb_cmd.group(1)
        bcb.handle_cmd(command)
        return
