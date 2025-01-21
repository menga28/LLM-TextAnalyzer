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
    .appName("CouchDBToSparkWithChangesFeed") \
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

# Variabili globali per tracciare l'ultima sequenza elaborata per ogni database
last_seq_ids = {
    "paperllm_content": "0",
    "paperllm_query": "0",
    "paperllm_results": "0"
}

def get_changes_from_couchdb(db_name, since_seq):
    """
    Recupera le modifiche da CouchDB usando il feed `_changes`, escludendo i documenti eliminati.
    """
    try:
        couch_server = Server(couchdb_url_with_credentials)
        couch_db = couch_server[db_name]

        # Recupera modifiche dal database
        changes = couch_db.changes(since=since_seq, include_docs=True)
        
        # Filtra solo le modifiche che non sono state eliminate
        valid_changes = [
            change for change in changes['results']
            if not change.get('deleted', False) and 'doc' in change
        ]

        logger.info(f"Recuperati {len(valid_changes)} documenti dal database {db_name}.")
        return valid_changes, changes.get('last_seq', since_seq)
    except Exception as e:
        logger.error(f"Errore nel recupero dei documenti da {db_name}: {e}")
        logger.error("Dettagli dell'errore:\n" + traceback.format_exc())
        return [], since_seq

def process_changes():
    """
    Processa le modifiche da ciascun database e aggiorna i DataFrame Spark.
    """
    global last_seq_ids
    for db_name, last_seq in last_seq_ids.items():
        valid_changes, new_last_seq = get_changes_from_couchdb(db_name, last_seq)
        
        if valid_changes:
            # Estrai gli ID direttamente dal feed `_changes`
            doc_ids = [change['id'] for change in valid_changes]
            # Logga gli ID dei documenti recuperati
            logger.info(f"Documenti trovati nel database {db_name}:")
            for doc_id in doc_ids:
                logger.info(f"  - {doc_id}")

            # Estrai i documenti effettivi dal campo `doc`
            documents = [change['doc'] for change in valid_changes if 'doc' in change]

            # Creazione del DataFrame Spark
            df = spark.createDataFrame(documents)
            df.createOrReplaceTempView(f"changes_couchdb_documents_{db_name}")
            logger.info(f"Tabella 'changes_couchdb_documents_{db_name}' aggiornata con {len(documents)} documenti.")
        else:
            logger.info(f"Nessun documento trovato nel database {db_name}.")

        # Aggiorna il valore di `last_seq` per il prossimo ciclo
        last_seq_ids[db_name] = new_last_seq

# Streaming Structured - Loop di aggiornamento
while True:
    try:
        process_changes()
    except Exception as e:
        logger.error(f"Errore nel ciclo di aggiornamento: {e}")
    
    # Attende 60 secondi prima di eseguire il prossimo polling
    time.sleep(60)
