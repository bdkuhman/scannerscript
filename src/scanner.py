#!/usr/bin/python

from command import *
from consts import *
from package import *
from device import *
from mode import *
from package import *
from upc import *
from util import *

from evdev import categorize, ecodes

import re


HA_URL = envvar("HA_URL")
HA_API_KEY = envvar("HA_API_KEY")

BBB_URL = envvar("BBB_URL")
BBB_API_KEY = envvar("BBB_API_KEY")

COMMAND_REGEX = envvar("CMD_REGEX", r"^_CMD:(.*)$")

def handle_input(input):
    # wake_screen()
    reset_mode()

    if input.startswith("BAT_VOL="):
        print(f"Battery: {input}")
        return

    if re.match(COMMAND_REGEX, input):
        handle_command(input)
        return

    for upcType, regexList in UPC_RGX_MAP.items():
        for regex in regexList:
            if re.match(regex, input):
                if handle_upc(upcType, input):
                    return
                else:
                    continue

    for courier, regexList in PKG_RGX_MAP.items():
        for regex in regexList:
            if re.match(regex, input):
                if handle_package(courier, input):
                    return
                else:
                    continue

    print(f"Unknown input: {input}")
    return





def scanner_loop():
    global scancodes

    device = load_device()

    # Default to lowercase
    scancodes = lowerscancodes

    # The barcode we read.
    barcode = ""

    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            eventdata = categorize(event)
            # print(eventdata)

            if eventdata.keystate == 1:  # Keydown
                scancode = eventdata.scancode
                if scancode == 28:
                    handle_input(barcode)
                    # Report what we scanned and reset
                    print(f">{barcode}<")
                    barcode = ""
                    # If we get a shift key
                elif scancode == 42 or scancode == 54:
                    # Swap to the upper codes
                    scancodes = upperscancodes
                else:
                    # Add to the current barcode
                    key = scancodes.get(scancode, NOT_RECOGNIZED_KEY)
                    barcode = barcode + key
                    # If we get an unknown key
                    if key == NOT_RECOGNIZED_KEY:
                        # Report what the original scancode was, so we can add it.
                        print("unknown key, scancode=" + str(scancode))
                    # Reset to lowercase again
                    scancodes = lowerscancodes




