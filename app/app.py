import time
import logging
import threading
from utils import result_xml_to_csv, query_xml_to_csv, content_xml_to_csv
#from spark_client import process_with_spark
from llm_service import process_with_llm, creating_llm
from config import get_model_by_id, MODEL_DIR
from utils import download_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

path_xml_dataset = "/datasets/"
model = get_model_by_id("llama-3.2-3b")
prompt = "How i can print in python and in java?"

def periodic_call():
    logging.info("Inizio del processo periodico.")
    # Converti XML in CSV
    #query_xml_to_csv(path_xml_dataset + "query.xml")
    #result_xml_to_csv(path_xml_dataset + "result.xml")
    #content_xml_to_csv(path_xml_dataset + "content.xml")

    # Invia i dati a Spark
    #process_with_spark(path_xml_dataset)
    
    # Chiamata a onprem.LLM
    logging.info(process_with_llm(prompt))

    logging.info("Processo periodico completato.\n")
    threading.Timer(60, periodic_call).start()


def main():
    logging.info("Applicazione avviata.")
    periodic_call()
    while True:
        time.sleep(1)

def initialize_model(model):
    try:
        logging.info(f"Model selected: {model}\n")
        creating_llm(model)
        logging.info(f"Model {model['id']} initialized successfully.")
    except ValueError as e:
        logging.error(f"Model initialization error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during model initialization: {e}")
        raise

if __name__ == "__main__":
    initialize_model(model)
    main()