from pyspark.sql import SparkSession
from couchdb import Server
import os
import logging
import time

# Configurazione del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione di Spark
spark = SparkSession.builder \
    .appName("CouchDBToSparkExample") \
    .getOrCreate()

# Recupero delle variabili d'ambiente per la connessione a CouchDB
couchdb_url = os.getenv("COUCHDB_URL")
couchdb_user = os.getenv("COUCHDB_USER")
couchdb_password = os.getenv("COUCHDB_PASSWORD")
couchdb_connection = f"http://{couchdb_user}:{couchdb_password}@{couchdb_url}"

# Log di connessione
logger.info(f"Connessione a CouchDB: {couchdb_connection}")

def read_from_couchdb():
    try:
        # Connessione al server CouchDB
        couch_server = Server(couchdb_connection)
        couch_db_name = 'paperllm'
        couch_db = couch_server[couch_db_name]
        logger.info(f"Connesso al database CouchDB: {couch_db_name}")

        # Recupera i documenti
        documents = [
            {
                "id": doc.id,
                **doc.doc
            }
            for doc in couch_db.view('_all_docs', include_docs=True)
        ]
        logger.info(f"Numero di documenti recuperati: {len(documents)}")
        return documents

    except Exception as e:
        logger.error(f"Errore durante la lettura dei documenti: {e}")
        return []

# Funzione per trasformare i documenti di CouchDB in un DataFrame
def create_dataframe_from_couchdb():
    documents = read_from_couchdb()
    if documents:
        return spark.createDataFrame(documents)
    else:
        logger.info("Nessun documento trovato.")
        return None

# Streaming Structured - Loop di aggiornamento
while True:
    df = create_dataframe_from_couchdb()
    if df:
        # Mostra i dati nel DataFrame
        df.show(truncate=False)
    else:
        logger.info("Nessun nuovo documento trovato in CouchDB.")

    # Attende 60 secondi prima di eseguire il prossimo polling
    time.sleep(60)