import time
import logging
import threading
import os
import requests
from utils import result_xml_to_csv, query_xml_to_csv, content_xml_to_csv
# from spark_client import process_with_spark
from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

path_xml_dataset = "/app/datasets/"
path_xml_dataset = os.path.join("datasets")

app = Flask(__name__)
ONPREM_LLM_URL = "http://onprem:5001"

def periodic_call():
    """
    Processo periodico per testare funzionalità e inviare richieste al modello.
    """
    logging.info("Inizio del processo periodico.")
    query_xml_to_csv(os.path.join(path_xml_dataset,"query.xml"))
    result_xml_to_csv(os.path.join(path_xml_dataset, "result.xml"))
    content_xml_to_csv(os.path.join(path_xml_dataset,"content.xml"))

    # process_with_spark(path_xml_dataset) 

    logging.info("Processo periodico completato.\n")

    threading.Timer(60, periodic_call).start()

@app.route('/status', methods=['GET'])
def status():
    """
    Controlla lo stato del server e del modello.
    """
    try:
        response = requests.get(f"{ONPREM_LLM_URL}/status", timeout=5)
        return response.json()
    except requests.exceptions.RequestException:
        return jsonify({"status": "error", "message": "OnPremLLM non raggiungibile."})

def main():
    """
    Avvia il server Flask e il processo periodico in un thread separato.
    """
    logging.info("🚀 Avvio di llm-app...")
    
    # Avvia periodic_call() in un thread separato
    thread = threading.Thread(target=periodic_call, daemon=True)
    thread.start()

    # Avvia il server Flask
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()