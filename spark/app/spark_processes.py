import os
import time
import logging
from pyspark.sql import SparkSession
from couchdb_utils import get_changes_from_couchdb, save_result_to_couchdb
import requests

# Configurazione del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione di Spark
spark = SparkSession.builder \
    .appName("CouchDBToSparkWithLLM") \
    .config("spark.executor.memory", "4g").config("spark.executor.cores", "2") \
    .getOrCreate()

# Variabili globali per tracciare l'ultima sequenza elaborata per ogni database
last_seq_ids = {
    "paperllm_content": "0",
    "paperllm_query": "0",
    "paperllm_results": "0"
}

import requests
import time

import requests
import time

def send_to_onprem_llm(query, abstract, max_retries=10, wait_time=5, timeout=90):
    """
    Invia una query e un abstract a OnPremLLM e restituisce la risposta.
    Se OnPremLLM non è ancora pronto, riprova fino a `max_retries`.
    """
    url = "http://app:5000/process"
    payload = {
    "query": query,
    "abstract": abstract
    }

    for attempt in range(max_retries):
        try:
            start_time = time.time()
            logger.info(f"📤 Invio richiesta a OnPremLLM con query='{query[:50]}...' e abstract='{abstract[:50]}...'")
            response = requests.post(url, json=payload, timeout=timeout)
            elapsed_time = time.time() - start_time  # Tempo di esecuzione della richiesta

            if response.status_code == 200:
                logger.info(f"✅ OnPremLLM ha risposto in {elapsed_time:.2f}s.")
                return response.json().get('response', "No response")
            else:
                logger.error(f"Errore API OnPremLLM: {response.status_code} {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ OnPremLLM non disponibile (tentativo {attempt + 1}/{max_retries}). Riprovo tra {wait_time}s...")
            time.sleep(wait_time)
        except requests.exceptions.ReadTimeout:
            logger.error(f"❌ Timeout di {timeout}s superato. OnPremLLM potrebbe essere lento. Riprovo tra {wait_time}s...")
            time.sleep(wait_time)

    logger.error("❌ OnPremLLM non raggiungibile dopo diversi tentativi.")
    return None

def process_queries_with_abstracts():
    """
    Esegue le query sugli abstract e invia i dati a OnPremLLM.
    """
    try:
        logger.info("🔵 2. Elaborazione delle query con OnPremLLM...")

        # ✅ Recupera le query dal database paperllm_query
        query_df = spark.sql("""
            SELECT _id AS query_id, text AS query_text, updated_at AS query_updated_at
            FROM changes_couchdb_documents_paperllm_query
        """)

        # ✅ Recupera gli abstract dal database paperllm_content
        content_df = spark.sql("""
            SELECT _id AS content_id, title, abstract AS content_text, updated_at AS content_updated_at
            FROM changes_couchdb_documents_paperllm_content
        """)

        if query_df.count() == 0 or content_df.count() == 0:
            logger.info("⚠️ Nessuna nuova query o abstract trovati.")
            return
        
        # ✅ Esegui il cross join per combinare ogni query con ogni abstract
        query_content_pairs = query_df.crossJoin(content_df)

        num_processed = 0
        for row in query_content_pairs.collect():
            query_id = row["query_id"]
            query_text = row["query_text"]  # ✅ Usa il nome corretto della colonna
            content_id = row["content_id"]
            abstract_text = row["content_text"]  # ✅ Usa il nome corretto della colonna

            logger.info(f"📝 Elaborazione query_id={query_id} con content_id={content_id}")

            # ✅ Chiama OnPremLLM con query e abstract
            response = send_to_onprem_llm(query_text, abstract_text)
            if response:
                save_result_to_couchdb(query_id, content_id, response, row["query_updated_at"], row["content_updated_at"])
                num_processed += 1

        logger.info(f"🟢 {num_processed} nuove query processate.")

    except Exception as e:
        logger.error(f"❌ Errore nel ciclo di elaborazione: {e}")

def process_changes():
    """
    Processa le modifiche da ciascun database e aggiorna i DataFrame Spark.
    """
    global last_seq_ids
    schemas = {
        "paperllm_content": "`_id` STRING, `title` STRING, `abstract` STRING, `updated_at` STRING",
        "paperllm_query": "`_id` STRING, `text` STRING, `updated_at` STRING",
        "paperllm_results": "`_id` STRING, `query_id` STRING, `content_id` STRING, `response` STRING, `query_updated_at` STRING, `content_updated_at` STRING"
    }

    for db_name in last_seq_ids.keys():
        valid_changes, new_last_seq = get_changes_from_couchdb(db_name, last_seq_ids[db_name])
        
        if valid_changes:
            documents = [change['doc'] for change in valid_changes if 'doc' in change]
            df = spark.createDataFrame(documents)
        else:
            # ✅ Se non ci sono nuovi documenti, creiamo una tabella vuota con lo schema corretto
            df = spark.createDataFrame([], schema=schemas[db_name])

        df.createOrReplaceTempView(f"changes_couchdb_documents_{db_name}")
        logger.info(f"Tabella 'changes_couchdb_documents_{db_name}' aggiornata con {len(valid_changes)} documenti.")

        last_seq_ids[db_name] = new_last_seq  # Aggiorna la sequenza

# ✅ **Unico ciclo principale**
while True:
    try:
        logger.info("🟢 1. Aggiornamento dati da CouchDB in Spark...")
        process_changes()  # Aggiorna Spark con nuovi dati

        logger.info("🔵 2. Elaborazione delle query con OnPremLLM...")
        process_queries_with_abstracts()  # Esegue le query sugli abstract

    except Exception as e:
        logger.error(f"❌ Errore nel ciclo di elaborazione: {e}")

    logger.info("⏳ Attesa 60 secondi per il prossimo ciclo...")
    time.sleep(60)
