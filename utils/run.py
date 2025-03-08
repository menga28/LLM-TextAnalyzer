import time
import logging
import threading
import os
import requests
from utils import result_xml_to_csv, query_xml_to_csv, content_xml_to_csv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

path_xml_dataset = "/datasets/"


def periodic_call():
    """
    Processo periodico per testare funzionalità e inviare richieste al modello.
    """
    logging.info("Inizio del processo periodico.")
    query_xml_to_csv(os.path.join(path_xml_dataset,"query.xml"))
    result_xml_to_csv(os.path.join(path_xml_dataset, "result.xml"))
    content_xml_to_csv(os.path.join(path_xml_dataset,"content.xml"))

    logging.info("Processo periodico completato.\n")

    threading.Timer(120, periodic_call).start()

def main():
    """
    Avvia il server Flask e il processo periodico in un thread separato.
    """
    logging.info("🚀 Avvio di llm-utils...")
    
    # Avvia periodic_call() in un thread separato
    thread = threading.Thread(target=periodic_call, daemon=True)
    thread.start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()