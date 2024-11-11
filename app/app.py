import time
import logging
import time
import threading
from utils import xml_flattener

def chiamata_periodica():
    xml_flattener()
    threading.Timer(5, xml_flattener).start()


def main():
    chiamata_periodica()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
