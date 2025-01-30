import time
import logging
import threading
from utils import result_xml_to_csv, query_xml_to_csv, content_xml_to_csv
#from spark_client import process_with_spark
from llm_service import process_with_llm, creating_llm
from config import get_model_by_id, MODEL_DIR, ACTUAL_MODEL
from utils import downloading_all_models
from flask import Flask, request, jsonify

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Percorso dataset XML
path_xml_dataset = "/datasets/"

# Inizializzazione del modello
model = get_model_by_id(ACTUAL_MODEL)

# Creazione del server Flask
app = Flask(__name__)


prompt = "How i can print in python and in java?"

def periodic_call():
    """
    Processo periodico per testare funzionalità e inviare richieste al modello.
    """
    logging.info("Inizio del processo periodico.")
    # Converti XML in CSV
    #query_xml_to_csv(path_xml_dataset + "query.xml")
    #result_xml_to_csv(path_xml_dataset + "result.xml")
    #content_xml_to_csv(path_xml_dataset + "content.xml")

    # Invia i dati a Spark
    #process_with_spark(path_xml_dataset)
    
    # Esempio di elaborazione con OnPrem.LLM
    response = process_with_llm(prompt)
    logging.info(f"Risposta da OnPrem.LLM: {response}")
    logging.info("Processo periodico completato.\n")
    
    threading.Timer(60, periodic_call).start()

@app.route('/process', methods=['POST'])
def process_prompt():
    """
    Endpoint REST per elaborare una query con un abstract.
    Riceve una query e un abstract in JSON e restituisce la risposta dell'LLM.
    """
    data = request.get_json()

    # ✅ LOG DI DEBUG PER VEDERE COSA VIENE RICEVUTO
    logger.info(f"📥 Ricevuto payload API: {data}")

    # ✅ Controlliamo che entrambi i campi siano presenti nel payload
    if not data or 'query' not in data or 'abstract' not in data:
        logger.error(f"❌ Errore: Payload JSON non valido - {data}")
        return jsonify({'error': 'I campi "query" e "abstract" sono obbligatori'}), 400

    query = data['query']
    abstract = data['abstract']

    # ✅ Formattiamo il prompt in modo chiaro per il modello LLM
    prompt = f"Domanda: {query}\n\nAbstract:\n{abstract}\n\nRisposta:"
    
    # ✅ Inviamo il prompt al modello LLM
    response = process_with_llm(prompt)

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
    #periodic_call() # Avvia il processo periodico
    app.run(host='0.0.0.0', port=5000)  # Avvia il server Flask

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
    downloading_all_models()  # Scarica tutti i modelli necessari
    initialize_model(model)  # Inizializza il modello attivo
    main()  # Avvia l'applicazione