from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from couchdb import Server
import os
import logging
import time

# Configurazione del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione di PySpark
spark = SparkSession.builder \
    .appName("CouchDBToSparkExample") \
    .getOrCreate()

# Configurazione dello Streaming (StreamingContext DEPRECATED since Spark 3.4.0)
ssc = StreamingContext(spark.sparkContext, 60)  # Stream ogni 10 secondi

# Recupero delle variabili d'ambiente per la connessione
couchdb_url = os.getenv("COUCHDB_URL")
couchdb_user = os.getenv("COUCHDB_USER")
couchdb_password = os.getenv("COUCHDB_PASSWORD")
couchdb_connection = f"http://{couchdb_user}:{couchdb_password}@{couchdb_url}"

# Log di connessione
logger.info(f"Connessione a CouchDB: {couchdb_connection}")

def read_from_couchdb():
    try:
        couch_server = Server(couchdb_connection)
        couch_db_name = 'paperllm'
        couch_db = couch_server[couch_db_name]
        logger.info(f"Connesso al database CouchDB: {couch_db_name}")

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

def process_rdd(time, rdd):
    logger.info(f"Elaborazione batch a: {time}")
    if not rdd.isEmpty():
        df = spark.createDataFrame(rdd.collect())
        df.show(truncate=False)

def monitor_couchdb():
    new_documents = read_from_couchdb()
    if new_documents:
        rdd = ssc.sparkContext.parallelize(new_documents)
        current_time = int(time.time() * 1000)  # Ottieni il tempo corrente in millisecondi
        process_rdd(current_time, rdd)
    else:
        logger.info("Nessun nuovo documento trovato")

# Usa una coda per simulare un flusso continuo di dati
dstream = ssc.queueStream([ssc.sparkContext.parallelize(read_from_couchdb())])

# Applica una funzione a ogni RDD nel DStream
dstream.foreachRDD(process_rdd)

# Avvia la computazione
ssc.start()

# Esegui il monitoraggio continuo
while True:
    monitor_couchdb()
    time.sleep(60)  # Attende 10 secondi tra ogni controllo

# Attendi l'arresto
ssc.awaitTermination()