import requests
import mode
from util import envvar, mapGet
from enum import Enum

import scanner

BCB_URL = envvar("BCB_URL")
BCB_API_KEY = envvar("BCB_API_KEY")


# BCB API states
class BCB_STATE(Enum):
    STATE_CONSUME = 0
    STATE_CONSUME_SPOILED = 1
    STATE_PURCHASE = 2
    STATE_OPEN = 3
    STATE_GETSTOCK = 4
    STATE_ADD_SL = 5
    STATE_CONSUME_ALL = 6


# BCB API Barcode types
BCB_STATE_CODES = {
    "BARCODE_C": BCB_STATE.STATE_CONSUME,
    "BARCODE_CS": BCB_STATE.STATE_CONSUME_SPOILED,
    "BARCODE_P": BCB_STATE.STATE_PURCHASE,
    "BARCODE_O": BCB_STATE.STATE_OPEN,
    "BARCODE_GS": BCB_STATE.STATE_GETSTOCK,
    "BARCODE_AS": BCB_STATE.STATE_ADD_SL,
    "BARCODE_CA": BCB_STATE.STATE_CONSUME_ALL,
    "BARCODE_Q": None,
}

# Internal states/keywords -> Barcode types
BCB_FUNC = {
    "consume": "BARCODE_C",  # 0
    "purchase": "BARCODE_P",  # 2
    "qty": "BARCODE_Q",  #
    "spoil": "BARCODE_CS",  # 1
    "open": "BARCODE_O",  # 3
    "shop": "BARCODE_AS",  # 5
    "all": "BARCODE_CA",  # 6
    "inventory": "BARCODE_GS",  # 4
}


# Current API Barcode types -> Barcodes (queried from the BCB api)
BCB_CODES = {}


def init():
    global BCB_CODES

    print(f"Initializing BCB. Getting command barcodes")
    BCB_CODES = get_commands()
    for k, v in BCB_FUNC.items():
        print(f"{k: <10} ({v} = {BCB_CODES[v]})")

    print(f"Current BCB state: {BCB_STATE(get_state()).name}")

    print("BCB Initialized.")


def switchMode(mode):
    print(f"Sending BCB mode string for {mode}")
    scan(mapGet(BCB_CODES, mapGet(BCB_FUNC, mode)))


def set_qty(qty):
    print(f"Setting quantity of next item to {qty}")
    barcode = mapGet(BCB_CODES, mapGet(BCB_FUNC, "qty")) + qty
    scan(barcode)


def get_state():
    resp = http_get("/state/getmode")
    return resp["data"]["mode"]


def scan(barcode):
    print(f"Sending barcode to BCB: {barcode}")
    url = "/action/scan"
    data = {"barcode": barcode}
    http_post(url, data)


def http_get(url):
    if BCB_URL is not None:
        url = BCB_URL + url
    else:
        print(f"{url}: Not sending request. Please specify BCB_URL")
        return
    print(f"GET: {url}")
    response = requests.get(url, headers={"BBUDDY-API-KEY": BCB_API_KEY})
    return handle_response(response)


def http_post(url, data):
    if BCB_URL is not None:
        url = BCB_URL + url
    else:
        print(f"{url}: Not sending request. Please specify BCB_URL")
        return
    print(f"POST: {url}")
    response = requests.post(url, data=data, headers={"BBUDDY-API-KEY": BCB_API_KEY})
    return handle_response(response)


def handle_response(response):
    if response.status_code == 404:
        print("404: Not Found")
    elif response.status_code == 401:
        print("401: Unauthorized")
        print("(is BCB_API_KEY correct?)")
    elif response.status_code != 200:
        data = response.json()
        print(data["result"]["result"])
    else:
        return response.json()
    return None


def get_commands():
    resp = http_get("/system/barcodes")
    # print(resp)
    return resp["data"]


def handle_cmd(command):
    # If it's one of the special barcodes.
    print("Handling command " + command)

    if mode.get_context() == mode.Context.BCB_QTY:
        # command is the quantity
        qty = command
        func =  mapGet(BCB_FUNC, "qty")
        print(f"Setting quantity to {int(qty)}")
        scan(mapGet(BCB_CODES, func) + qty)
        mode.reset()
        return
    
    elif command == "qty":
        # qty needs more data.
        print("Setting barcodebuddy quantity, Please scan a number")
        mode.set_context(mode.Context.BCB_QTY)
    elif command == "qstate":
        print(BCB_STATE(get_state()))
    elif command == "qcodes":
        print(get_commands())
    else:
        func = mapGet(BCB_FUNC, command)
    
        if mapGet(BCB_STATE_CODES, func) is not None:
            # We can directly pass these ones.
            scan(mapGet(BCB_CODES, func))
        else:
            print(f"Unknown BCB command: {command}")
