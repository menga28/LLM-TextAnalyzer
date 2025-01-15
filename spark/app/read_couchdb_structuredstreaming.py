import os
import traceback
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

# Variabili globali per tracciare l'ultimo documento elaborato per ogni database
last_doc_ids = {
    "paperllm_content": None,
    "paperllm_query": None,
    "paperllm_result": None
}

def read_from_couchdb(db_name, startkey=None):
    """
    Legge i documenti da CouchDB, eventualmente filtrando a partire da un ID specifico.
    """
    try:
        couch_server = Server(couchdb_url_with_credentials)
        couch_db = couch_server[db_name]
        logger.info(f"Connesso al database CouchDB: {db_name}")

        # Filtro opzionale con startkey
        view_params = {'include_docs': True}
        if startkey:
            view_params['startkey_docid'] = startkey

        documents = []
        startkey_found = startkey is None
        for row in couch_db.view('_all_docs', **view_params):
            doc_id = row['id'] 
            doc = row.get('doc') 
            if doc: 
                if startkey and doc_id == startkey: # Salta il documento con ID uguale alla startkey 
                    continue 
                documents.append({ 
                    "id": doc_id, 
                    **doc
                })

        logger.info(f"Numero totale di documenti recuperati da {db_name}: {len(documents)}")
        return documents

    except Exception as e:
        logger.error(f"Errore durante la lettura dei documenti da {db_name}: {e}")
        logger.error("Dettagli dell'errore:\n" + traceback.format_exc())
        return []

def initialize_last_doc_ids():
    """
    Inizializza l'ID dell'ultimo documento esistente in ciascun database.
    """
    global last_doc_ids
    for db_name in last_doc_ids.keys():
        documents = read_from_couchdb(db_name)
        if documents:
            # Usa l'ultimo documento recuperato
            last_doc_ids[db_name] = documents[-1]['id']
            logger.info(f"Initial last_doc_id for {db_name} set to: {last_doc_ids[db_name]}")
        else:
            logger.warning(f"Nessun documento trovato per inizializzare last_doc_id in {db_name}.")
            last_doc_ids[db_name] = None

def process_new_documents():
    """
    Elabora i nuovi documenti dai database e aggiorna i DataFrame Spark.
    """
    global last_doc_ids
    for db_name, last_doc_id in last_doc_ids.items():
        documents = read_from_couchdb(db_name, startkey=last_doc_id) if last_doc_id else read_from_couchdb(db_name)
        # Log del valore di startkey per il debug
        logger.info(f"Recuperando documenti da {db_name} con startkey: {last_doc_id}")

         # Log per verificare se sono stati recuperati documenti
        if len(documents) == 0:
            logger.warning(f"Database {db_name} sembra essere vuoto o il filtro ha escluso tutti i documenti.")
        else:
            logger.info(f"Numero totale di documenti recuperati da {db_name}: {len(documents)}")

        if documents:
            # Filtra solo documenti nuovi
            new_documents = [doc for doc in documents if doc['id'] != last_doc_id]
            logger.info(f"Documenti nuovi trovati in {db_name}: {len(new_documents)}")

            if new_documents:
                df_new = spark.createDataFrame(new_documents)
                df_new.createOrReplaceTempView(f"new_couchdb_documents_{db_name}")
                logger.info(f"Tabella 'new_couchdb_documents_{db_name}' registrata con {len(new_documents)} righe.")
                
                # Visualizza le prime 5 righe della nuova tabella
                query_df_new = spark.sql(f"SELECT * FROM new_couchdb_documents_{db_name} LIMIT 5")
                query_df_new.show(truncate=False)
                
                # Aggiorna last_doc_id all'ultimo ID elaborato
                last_doc_ids[db_name] = new_documents[-1]['id']
            else:
                logger.info(f"Nessun nuovo documento trovato in {db_name}.")
        else:
            logger.info(f"Nessun documento recuperato da {db_name}.")

# Inizializza gli ultimi ID
initialize_last_doc_ids()

# Streaming Structured - Loop di aggiornamento
while True:
    try:
        process_new_documents()
    except Exception as e:
        logger.error(f"Errore nel ciclo di aggiornamento: {e}")
    
    # Attende 60 secondi prima di eseguire il prossimo polling
    time.sleep(60)
