import time
import logging
import time
import threading
from utils import result_xml_to_csv, query_xml_to_csv, content_xml_to_csv

path_xml_dataset = "/datasets/"


def chiamata_periodica():
    query_xml_to_csv(path_xml_dataset+"query.xml")
    result_xml_to_csv(path_xml_dataset+"result.xml")
    content_xml_to_csv(path_xml_dataset+"content.xml")
    threading.Timer(5, chiamata_periodica).start()


def main():
    chiamata_periodica()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
