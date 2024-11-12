import time
import logging
import time
import threading
from utils import create_dataframe_from_xml

path_xml_dataset = "/datasets/result.xml"


def chiamata_periodica():
    create_dataframe_from_xml(path_xml_dataset)
    threading.Timer(5, chiamata_periodica).start()


def main():
    chiamata_periodica()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
