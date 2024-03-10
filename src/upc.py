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
    


def validate_isbn_10(code):
    s = 0
    for i, xi in enumerate(code):
        s += (11 - i - 1) * (10 if xi in 'xX' else int(xi))

    return s % 11 == 0

