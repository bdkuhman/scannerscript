from util import envvar
from consts import lowerscancodes, upperscancodes
from evdev import InputDevice, InputEvent, ecodes
import sys
from types import SimpleNamespace as sn


def load_device():
    DEVICE_PATH = envvar("DEVICE_PATH")  # "/dev/input/by-id/usb-NT_USB_Keyboard-event-kbd"
    if DEVICE_PATH is not None:
        device = InputDevice(DEVICE_PATH)
        device.grab()
    else:
        # todo mock device when testing.
        # device = type('obj', (object,), {})
        import itertools

        # Flip lower scancodes
        invcodes = {v: [k] for k, v in lowerscancodes.items()}
        # add the upper scancodes to the list, but add shift before them, unless they're also in lowerscancodes
        for k, v in upperscancodes.items():
            if lowerscancodes[k] != v:
                invcodes[v] = [invcodes["RSHFT"][0], k]

        # Add the newline character
        invcodes["\n"] = invcodes["CRLF"]

        # Grab the commandline input or default to emptystr, and add the \n to complete the input
        input = (sys.argv[1] if len(sys.argv) > 1 else "") + "\n"

        # map to a list of list of keypresses, then create an chain that will unpack them.
        chn = itertools.chain(*[invcodes[ch] for ch in input])
        # Create a mock device that will return each keypress as an InputEvent object for the next keypress in the chain when read_loop is called.
        device = sn(
            read_loop=lambda: (
                InputEvent(0, 0, ecodes.EV_KEY, keypress, 1) for keypress in chn
            )
        )
        print("No device specified. Provide path through 'DEVICE_PATH' env var.")
        # exit(1)
    print("Scanner Ready!!")
    return device
