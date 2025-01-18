import time
import logging
import threading
from utils import result_xml_to_csv, query_xml_to_csv, content_xml_to_csv
#from spark_client import process_with_spark
from llm_service import process_with_llm

# Configura logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

path_xml_dataset = "/datasets/"

prompt = "How i can print in python and in java?"

def periodic_call():
    logging.info("Inizio del processo periodico.")
    
    # Converti XML in CSV
    query_xml_to_csv(path_xml_dataset + "query.xml")
    result_xml_to_csv(path_xml_dataset + "result.xml")
    content_xml_to_csv(path_xml_dataset + "content.xml")

    # Invia i dati a Spark
    #process_with_spark(path_xml_dataset)
    
    # Chiamata a onprem.LLM
    logging.info(process_with_llm(prompt))

    logging.info("Processo periodico completato.")
    threading.Timer(60, periodic_call).start()


def main():
    logging.info("Applicazione avviata.")
    periodic_call()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()