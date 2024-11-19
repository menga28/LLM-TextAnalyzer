import os
from couchdb import Server
from pyspark.sql import SparkSession
import logging
import time

# Configurazione del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione di Spark
spark = SparkSession.builder \
    .appName("CouchDBToSparkExample") \
    .config("spark.executor.memory", "4g").config("spark.executor.cores", "2") \
    .getOrCreate()

# Recupero delle variabili d'ambiente
couchdb_url = os.getenv("COUCHDB_URL")
couchdb_user = os.getenv("COUCHDB_USER")
couchdb_password = os.getenv("COUCHDB_PASSWORD")

if not couchdb_user or not couchdb_password:
    logger.error("Credenziali CouchDB non trovate. Assicurati di impostare COUCHDB_USER e COUCHDB_PASSWORD.")
    exit(1)

# Creazione dell'URL completo
couchdb_url_with_credentials = f"http://{couchdb_user}:{couchdb_password}@{couchdb_url}"

# Variabile globale per tracciare l'ultimo documento elaborato
last_doc_id = None

def read_from_couchdb(startkey=None):
    """
    Legge i documenti da CouchDB, eventualmente filtrando a partire da un ID specifico.
    """
    try:
        couch_server = Server(couchdb_url_with_credentials)
        couch_db_name = 'paperllm'
        couch_db = couch_server[couch_db_name]
        logger.info(f"Connesso al database CouchDB: {couch_db_name}")

        # Filtro opzionale con startkey
        view_params = {'include_docs': True}
        if startkey:
            view_params['startkey'] = startkey

        documents = [
            {
                "id": row['id'],
                **row['doc']
            }
            for row in couch_db.view('_all_docs', **view_params)
        ]
        logger.info(f"Numero di documenti recuperati: {len(documents)}")
        return documents

    except Exception as e:
        logger.error(f"Errore durante la lettura dei documenti: {e}")
        return []

def initialize_last_doc_id():
    """
    Inizializza l'ID dell'ultimo documento esistente nel database.
    """
    global last_doc_id
    documents = read_from_couchdb()
    if documents:
        last_doc_id = documents[-1]['id']
        logger.info(f"Initial last_doc_id set to: {last_doc_id}")
    else:
        logger.warning("No documents found to initialize last_doc_id.")

def process_new_documents():
    """
    Elabora i nuovi documenti dal database e aggiorna il DataFrame Spark.
    """
    global last_doc_id
    documents = read_from_couchdb(startkey=last_doc_id) if last_doc_id else read_from_couchdb()

    if documents:
        # Filtra solo documenti nuovi
        new_documents = [doc for doc in documents if doc['id'] != last_doc_id]
        if new_documents:
            df_new = spark.createDataFrame(new_documents)
            df_new.createOrReplaceTempView("new_couchdb_documents")
            logger.info(f"Tabella 'new_couchdb_documents' registrata con {len(new_documents)} righe.")
            
            # Visualizza le prime 5 righe della nuova tabella
            query_df_new = spark.sql("SELECT * FROM new_couchdb_documents LIMIT 5")
            query_df_new.show(truncate=False)
            
            # Aggiorna last_doc_id all'ultimo ID elaborato
            last_doc_id = new_documents[-1]['id']
        else:
            logger.info("Nessun nuovo documento trovato.")
    else:
        logger.info("Nessun documento recuperato.")

# Inizializza l'ultimo ID
initialize_last_doc_id()

# Streaming Structured - Loop di aggiornamento
while True:
    try:
        process_new_documents()
    except Exception as e:
        logger.error(f"Errore nel ciclo di aggiornamento: {e}")
    
    # Attende 60 secondi prima di eseguire il prossimo polling
    time.sleep(60)
