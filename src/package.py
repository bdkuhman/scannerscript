PKG_RGX_MAP = {
    "Amazon": [r"TBA[0-9]{12}"],
    "UPS": [r"\b1Z[A-Z0-9]{16}\b"],
    "USPS": [
        r"\b([A-Z]{2}\d{9}[A-Z]{2}|(420\d{9}(9[2345])?)?\d{20}|(420\d{5})?(9[12345])?(\d{24}|\d{20})|82\d{8})\b"
    ],
    "FedEx": [r"\b([0-9]{12}|100\d{31}|\d{15}|\d{18}|96\d{20}|96\d{32})\b"],
}

def handle_package(courier, trackingnum):
    print(f"Scanned {courier} package with Tracking Number {trackingnum}")
    return True
