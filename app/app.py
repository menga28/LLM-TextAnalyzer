import time
import logging
import time
import threading
from utils import minify_query_xml

path_xml_dataset = "/datasets/"


def chiamata_periodica():
    minify_query_xml(path_xml_dataset+"query.xml")
    
    threading.Timer(5, chiamata_periodica).start()


def main():
    chiamata_periodica()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
