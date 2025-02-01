import time
import logging
import threading
from utils import result_xml_to_csv, query_xml_to_csv, content_xml_to_csv
# from spark_client import process_with_spark
from llm_service import process_with_llm, creating_llm
from config import get_model_by_id, MODEL_DIR, ACTUAL_MODEL
from utils import downloading_all_models
from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

path_xml_dataset = "/datasets/"

model = get_model_by_id(ACTUAL_MODEL)

app = Flask(__name__)


def periodic_call():
    """
    Processo periodico per testare funzionalità e inviare richieste al modello.
    """
    logging.info("Inizio del processo periodico.")
    query_xml_to_csv(path_xml_dataset + "query.xml")
    result_xml_to_csv(path_xml_dataset + "result.xml")
    content_xml_to_csv(path_xml_dataset + "content.xml")

    # process_with_spark(path_xml_dataset)
    # response = process_with_llm(prompt)
    # logging.info(f"Risposta da OnPrem.LLM: {response}")

    logging.info("Processo periodico completato.\n")

    threading.Timer(60, periodic_call).start()


@app.route('/process', methods=['POST'])
def process_prompt():
    """
    Endpoint REST per elaborare una query con un abstract.
    Riceve una query e un abstract in JSON e restituisce la risposta dell'LLM.
    """
    data = request.get_json()

    logger.info(f"📥 Ricevuto payload API: {data}")

    if not data or 'query' not in data or 'abstract' not in data:
        logger.error(f"❌ Errore: Payload JSON non valido - {data}")
        return jsonify({'error': 'I campi "query" e "abstract" sono obbligatori'}), 400

    query = data['query']
    abstract = data['abstract']

    prompt = f"Domanda: {query}\n\nAbstract:\n{abstract}\n\nRisposta:"

    logging.ingo(prompt)

    # response = process_with_llm(prompt)
    response = "a"

    if response is None:
        return jsonify({'error': 'Errore durante l\'elaborazione del prompt'}), 500

    return jsonify({'response': response})


@app.route('/status', methods=['GET'])
def status():
    """
    Endpoint REST per controllare lo stato del server e del modello.
    """
    status_info = {
        'status': 'ok',
        'model': model['id'],
        'message': 'Il server è attivo e pronto a rispondere ai prompt.'
    }
    return jsonify(status_info)


def main():
    """
    Avvio dell'applicazione.
    """
    logging.info("Applicazione avviata.")
    # periodic_call() # Avvia il processo periodico
    app.run(host='0.0.0.0', port=5000)


def initialize_model(model):
    """
    Inizializza il modello selezionato.
    """
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
    # downloading_all_models()
    # initialize_model(model)
    main()