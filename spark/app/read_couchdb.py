from pyspark.sql import SparkSession
from couchdb import Server
import os
import json
import logging

# Configurazione del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione di PySpark
spark = SparkSession.builder \
    .appName("CouchDBToSparkExample") \
    .getOrCreate()

# Recupero delle variabili d'ambiente per la connessione
couchdb_url = os.getenv("COUCHDB_URL")
couchdb_user = os.getenv("COUCHDB_USER")
couchdb_password = os.getenv("COUCHDB_PASSWORD")
couchdb_connection = f"http://{couchdb_user}:{couchdb_password}@{couchdb_url}"

# Log di connessione
logger.info(f"Connessione a CouchDB: {couchdb_connection}")

# Connessione a CouchDB
try:
    couch_server = Server(couchdb_connection)
    couch_db_name = 'paperllm'
    couch_db = couch_server[couch_db_name]
    logger.info(f"Connesso al database CouchDB: {couch_db_name}")
except Exception as e:
    logger.error(f"Errore durante la connessione a CouchDB: {e}")
    spark.stop()
    exit(1)

# Leggere tutti i documenti dal database
try:
    documents = [
        {
            "id": doc.id,
            **doc.doc
        }
        for doc in couch_db.view('_all_docs', include_docs=True)
    ]
    logger.info(f"Numero di documenti recuperati: {len(documents)}")
except Exception as e:
    logger.error(f"Errore durante la lettura dei documenti: {e}")
    spark.stop()
    exit(1)

# Creazione del DataFrame Spark
try:
    df = spark.createDataFrame(documents)
    logger.info("DataFrame Spark creato con successo.")
    df.show(truncate=False)  # Mostra i dati
except Exception as e:
    logger.error(f"Errore durante la creazione del DataFrame Spark: {e}")

# Chiudi la sessione di Spark
spark.stop()
logger.info("Sessione Spark chiusa.")
