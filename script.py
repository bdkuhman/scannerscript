#!/usr/bin/python
# import signal, sys
# import json
# import requests
import re

import os

from evdev import InputDevice, categorize, ecodes

# import paho.mqtt.client as mqtt
import time

# import threading


# Originally used when this was running on an rpi.
# This script is now headless...
# def wake_screen():
#     os.system("xset -display :0.0 s reset && xset -display :0.0 dpms force on")


# def off_screen():
#     os.system("xset -display :0.0 s activate && xset -display :0.0 dpms force off")


# def rotate_screen():
#     os.system("DISPLAY=:0 xrandr -o left")


##mqtt stuffs

# Originally implemented to be able to rotate/wake the screen when on a rpi.
# Don't need mqtt things for now...

# topic_name="topic"

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))

#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe([(topic_name, 1)])


# def on_message(client, userdata, message):
#     print("Message received: " + message.topic + " : " + str(message.payload.decode()))
#     if message.topic == topic_name:
#         msg = message.payload.decode()
#         if msg == "wakeup":
#             wake_screen()
#         elif msg == "off":
#             off_screen()
#         elif msg == "rotate":
#             rotate_screen()
#         # with open('/home/pi/mqtt_update.txt', 'a+') as f:
#         #    f.write("received topic2")


# def mqtt_loop():
#     client.loop_forever()

# TODO: Pass in through env.
# broker_address = ""  # Broker address
# port = 1883  # Broker port
# user = ""  # Connection username
# password = ""  # Connection password


# client = mqtt.Client()  # create new instance
# client.username_pw_set(user, password=password)  # set username and password
# client.on_connect = on_connect  # attach function to callback
# client.on_message = on_message  # attach function to callback

# client.connect(broker_address, port=port)  # connect to broker

# client.loop_forever()

barcode = ""


def envvar(key, default=None):
    return os.environ.get(key, default)


DEVICE_PATH = envvar("DEVICE_PATH")  # "/dev/input/by-id/usb-NT_USB_Keyboard-event-kbd"

HA_URL = envvar("HA_URL")
HA_API_KEY = envvar("HA_API_KEY")
BBB_URL = envvar("BBB_URL")
BBB_API_KEY = envvar("BBB_API_KEY")

COMMAND_REGEX = envvar("CMD_REGEX", r"^_CMD:(.*)$")
MODE_REGEX = envvar("MODE_REGEX", r"^_CMD:MODE=(.*)$")

device = InputDevice(DEVICE_PATH)  # Replace with your device
device.grab()

# fmt: off
lowerscancodes = {
    # Scancode: ASCIICode
    0: None,
    1: "ESC", 2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9", 11: "0", 12: "-", 13: "=", 14: "BKSP",
    15: "TAB", 16: "q", 17: "w", 18: "e", 19: "r", 20: "t", 21: "y", 22: "u", 23: "i", 24: "o", 25: "p", 26: "[", 27: "]",
    28: "CRLF", 29: "LCTRL", 30: "a", 31: "s", 32: "d", 33: "f", 34: "g", 35: "h", 36: "j", 37: "k", 38: "l", 39: ";", 40: "'", 41: "`",
    42: "LSHFT", 43: "\\", 44: "z", 45: "x", 46: "c", 47: "v", 48: "b", 49: "n", 50: "m", 51: ",", 52: ".", 53: "/", 54: "RSHFT",
    56: "LALT", 57: " ", 100: "RALT"
}

upperscancodes = {
    # Scancode: ASCIICode
    0: None,
    1: "ESC", 2: "!", 3: "@", 4: "#", 5: "$", 6: "%", 7: "^", 8: "&", 9: "*", 10: "(", 11: ")", 12: "_", 13: "+", 14: "BKSP",
    15: "TAB", 16: "Q", 17: "W", 18: "E", 19: "R", 20: "T", 21: "Y", 22: "U", 23: "I", 24: "O", 25: "P", 26: "{", 27: "}", 
    28: "CRLF", 29: "LCTRL", 30: "A", 31: "S", 32: "D", 33: "F", 34: "G", 35: "H", 36: "J", 37: "K", 38: "L", 39: ":", 40: '"', 41: "~",
    42: "LSHFT", 43: "|", 44: "Z", 45: "X", 46: "C", 47: "V", 48: "B", 49: "N", 50: "M", 51: "<", 52: ">", 53: "?", 54: "RSHFT",
    56: "LALT", 57: " ", 100: "RALT"
}
#fmt on

scancodes = lowerscancodes

scannermode = "idle"
lastscan = time.time()

# TODO: Pass these through.
NOT_RECOGNIZED_KEY = "[?]"


PKG_RGX_MAP = {
    "Amazon": [r"TBA[0-9]{12}"],
    "UPS": [r"\b1Z[A-Z0-9]{16}\b"],
    "USPS": [
        r"\b([A-Z]{2}\d{9}[A-Z]{2}|(420\d{9}(9[2345])?)?\d{20}|(420\d{5})?(9[12345])?(\d{24}|\d{20})|82\d{8})\b"
    ],
    "FedEx": [r"\b([0-9]{12}|100\d{31}|\d{15}|\d{18}|96\d{20}|96\d{32})\b"],
}

UPC_RGX_MAP = {
    "UPC-A": [r"^[0-9]{12}$"],
    "UPC-E": [r"^[01][0-9]{7}$"],
    "ISBN-13": [r"^(97)(8|9)[0-9]{10}$"],
    "ISBN-10": [r"^[0-9]{9}[0-9xX]$"],
    "EAN-13": [r"^[0-9]{13}$"],
}


def handle_ean_etc(type, code):
    if type == "ISBN-10":
        if validate_isbn_10(code):
            print("Valid ISBN-10")
            return True

    if type == "ISBN-13":
        if validate_ean(code):
            print("Valid ISBN-13")
            return True

    if type == "EAN-13":
        if validate_ean(code[1:]):
            print("Valid EAN-13")
            return True

    return False


def handle_package(courier, trackingnum):
    print(f"Scanned {courier} package with Tracking Number {trackingnum}")
    return True


def validate_isbn_10(code):
    i = 0
    t = 0
    s = 0
    for i in range(10):
        t += code[i]
        s += t

    return s % 11 == 0


# upc but evens and odds swapped.
def validate_ean(code):
    parts = [int(c) for c in code]
    odds = parts[1::2]
    evens = parts[0::2]
    subtotal = (3 * sum(odds)) + sum(evens)
    return subtotal % 10 == 0


def validate_upc_a(code):
    parts = [int(c) for c in code]
    evens = parts[1::2]
    odds = parts[0::2]
    subtotal = (3 * sum(odds)) + sum(evens)

    return subtotal % 10 == 0


def validate_upc_e(code):
    upca = convert_upc_e_to_a(code)
    print(upca)
    return validate_upc_a(upca)


def convert_upc_e_to_a(code):
    upce = code[0:-1]
    print(f"upce: {upce}")
    if (int(upce[-1])) < 3:
        return upce[0:3] + upce[-1] + "0000" + upce[3:6] + code[-1]
    if (int(upce[-1])) == 3:
        return upce[0:4] + "00000" + upce[4:6] + code[-1]
    if (int(upce[-1])) == 4:
        return upce[0:5] + "00000" + upce[5] + code[-1]
    if (int(upce[-1])) > 4:
        return upce[0:6] + "0000" + upce[-1] + code[-1]


def handle_upc(type, code):
    print(f"Possible {type}: {code}")
    if type == "UPC-A":
        if validate_upc_a(code):
            print("Processing UPC-A")
            return True
        else:
            print("Not a valid UPC-A code")
            return False
    elif type == "UPC-E":
        if validate_upc_e(code):
            print("Processing UPC-E")
            return True
        else:
            print("Not a valid UPC-E code")
            return False
    elif type.startswith("ISBN") or type == "EAN-13":
        return handle_ean_etc(type, code)

def handle_command(input):
    print(f"COMMAND: {input}")
    global scannermode
    mode = re.match(MODE_REGEX, input)
    if mode:
        scannermode = mode.group(1)
        print(f"SET scannermode to {scannermode}")


def handle_input(input):
    # wake_screen()
    reset_mode()

    if input == "restart!":
        exit(1)

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


def scanner_loop():
    global scancodes
    global upperscancodes
    global lowerscancodes
    global barcode
    print("Scanner Ready!!")
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            eventdata = categorize(event)
            if eventdata.keystate == 1:  # Keydown
                scancode = eventdata.scancode
                if scancode == 28:  # Enter
                    print(f">{barcode}<")
                    handle_input(barcode)
                    barcode = ""
                elif scancode == 42 or scancode == 54:
                    scancodes = upperscancodes
                else:
                    key = scancodes.get(scancode, NOT_RECOGNIZED_KEY)
                    barcode = barcode + key
                    if key == NOT_RECOGNIZED_KEY:
                        print("unknown key, scancode=" + str(scancode))
                    scancodes = lowerscancodes


def reset_mode():
    global scannermode
    global lastscan

    now = time.time()
    diff = now - lastscan

    print(f"Last scan {diff}s ago")

    if (now - lastscan) >= 180:  # 3 minutes
        print("resetting scan mode")
        scannermode = "idle"
        lastscan = now


# mqttthread = threading.Thread(target=mqtt_loop, args="")
# scannerthread = threading.Thread(target=scanner_loop())
# mqttthread.start()
scanner_loop()
# scannerthread.start()
# mqttthread.join()
