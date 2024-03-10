#!/bin/python3
from scanner import *

def main():
    # mqttthread = threading.Thread(target=mqtt_loop, args="")
    # scannerthread = threading.Thread(target=scanner_loop())
    # mqttthread.start()
    scanner_loop()
    # scannerthread.start()
    # mqttthread.join()


if __name__ == "__main__":
    main()