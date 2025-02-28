import os
import time
import logging
from pyspark.sql import SparkSession
from couchdb_utils import get_changes_from_couchdb, save_result_to_couchdb
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Numero massimo di query consecutive per un modello prima di cambiarlo.
MAX_QUERIES_PER_MODEL = 10

# Inizializza Spark
spark = SparkSession.builder \
    .appName("CouchDBToSparkWithLLM") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", "2") \
    .getOrCreate()

# Riduce la verbosità dei log di Spark
spark.sparkContext.setLogLevel("WARN")


def get_available_models():
    """
    Recupera la lista dei modelli disponibili da OnPrem via API.
    """
    url = "http://onprem:5001/models"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("models", [])
        else:
            logger.error(
                f"Errore nel recupero dei modelli: {response.status_code} {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Errore nella richiesta dei modelli: {e}")
        return []


def set_onprem_model_and_wait(model_id, max_wait=3600, check_interval=5):
    """
    1) Richiama /set_model per impostare il modello su OnPrem (timeout 120s).
    2) Esegue un polling di /status finché:
       - /status non restituisce {status: "ok"} (modello pronto)
       - oppure non scade il tempo max_wait (di default 1 ora).
    Se dopo max_wait il modello non è pronto, logga un errore e termina la funzione.
    """
    url_set_model = f"http://onprem:5001/set_model?model_id={model_id}"
    try:
        logger.info(f"🔄 set_onprem_model_and_wait: POST {url_set_model}")
        # Aumenta il timeout se caricare il modello può richiedere molto
        r = requests.post(url_set_model, timeout=120)
        if r.status_code != 200:
            logger.warning(
                f"⚠️ /set_model ha ritornato {r.status_code}: {r.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Errore chiamando /set_model per '{model_id}': {e}")
        return

    url_status = "http://onprem:5001/status"
    waited = 0
    while waited < max_wait:
        try:
            resp = requests.get(url_status, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    logger.info(
                        f"✅ Modello '{model_id}' risulta ora caricato su OnPrem.")
                    return
                else:
                    logger.info(
                        f"⏳ Modello '{model_id}' in caricamento (status='{data.get('status')}')...")
            else:
                logger.warning(
                    f"⚠️ /status ha ritornato codice {resp.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Errore durante polling /status: {e}")

        time.sleep(check_interval)
        waited += check_interval

    logger.error(
        f"❌ Il modello '{model_id}' non si è caricato entro {max_wait} secondi.")


def send_to_onprem_llm(query, abstract, model_id, max_retries=10, wait_time=5, timeout=300):
    """
    Invia una query e un abstract a OnPremLLM specificando il modello
    (che dovrebbe già essere impostato correttamente su OnPrem).
    """
    url = "http://onprem:5001/infer"
    payload = {
        "model_id": model_id,
        "prompt": f"{query}\n\nAbstract: {abstract}"
    }

    for attempt in range(max_retries):
        try:
            start_time = time.time()
            logger.info(f"📤 [{model_id}] Invio richiesta a OnPremLLM...")
            response = requests.post(url, json=payload, timeout=timeout)
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                logger.info(
                    f"✅ [{model_id}] OnPremLLM ha risposto in {elapsed_time:.2f}s.")
                return response.json().get('response', "No response")
            else:
                logger.error(
                    f"❌ [{model_id}] Errore API OnPremLLM: {response.status_code} {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            logger.warning(
                f"⚠️ [{model_id}] OnPremLLM non disponibile (tentativo {attempt + 1}/{max_retries}). Riprovo...")
            time.sleep(wait_time)
        except requests.exceptions.ReadTimeout:
            logger.error(f"❌ [{model_id}] Timeout di {timeout}s superato.")
            time.sleep(wait_time)

    logger.error(
        f"❌ [{model_id}] OnPremLLM non raggiungibile dopo {max_retries} tentativi.")
    return None


def build_query_queue(query_df, content_df, models):
    """
    Costruisce una coda di tuple (model_id, query_id, query_text, content_id, abstract_text, q_upd, c_upd).
    Poi la ordina per model_id, così inviamo batch di query per ogni modello.
    """
    queue = []
    # Uniamo query e content (prodotto cartesiano)
    query_content_pairs = query_df.crossJoin(content_df).collect()

    for row in query_content_pairs:
        for m in models:
            queue.append((
                m,
                row["query_id"],
                row["query_text"],
                row["content_id"],
                row["content_text"],
                row["query_updated_at"],
                row["content_updated_at"]
            ))

    # Ordina per model_id
    queue.sort(key=lambda x: x[0])
    return queue


def process_queries_with_abstracts():
    """
    Esegue le query su ogni abstract, raggruppate per modello.
    Le query vengono eseguite se non esistono già in changes_couchdb_documents_paperllm_results.
    Verifica lo stato corrente di OnPremLLM tramite l'endpoint /status e,
    se il modello attivo (current_model) non corrisponde a quello richiesto,
    invoca set_onprem_model_and_wait per caricare il modello corretto.
    """
    try:
        logger.info("🔵 2. Elaborazione delle query con OnPremLLM...")

        # 1) Recuperiamo i modelli disponibili
        models = get_available_models()
        if not models:
            logger.error("❌ Nessun modello disponibile per eseguire le query.")
            return

        # 2) Leggiamo query e content da Spark
        query_df = spark.sql("""
            SELECT _id AS query_id, text AS query_text, updated_at AS query_updated_at
            FROM changes_couchdb_documents_paperllm_query
        """)

        content_df = spark.sql("""
            SELECT _id AS content_id, title, abstract AS content_text, updated_at AS content_updated_at
            FROM changes_couchdb_documents_paperllm_content
        """)

        existing_results_df = spark.sql("""
            SELECT query_id, content_id, model_id
            FROM changes_couchdb_documents_paperllm_results
        """)
        existing_results = {
            (row["query_id"], row["content_id"], row["model_id"])
            for row in existing_results_df.collect()
        }

        queue = build_query_queue(query_df, content_df, models)

        # Filtriamo le query da eseguire: solo quelle per cui non esiste già un risultato
        filtered_queue = []
        for (m_id, q_id, q_text, c_id, c_text, q_upd, c_upd) in queue:
            if (q_id, c_id, m_id) not in existing_results:
                filtered_queue.append((m_id, q_id, q_text, c_id, c_text, q_upd, c_upd))

        if not filtered_queue:
            logger.info("⚠️ Nessuna nuova query o abstract da processare dopo il filtraggio.")
            return

        logger.info(f"🗒 filtered_queue contiene {len(filtered_queue)} elementi: {filtered_queue}")

        current_onprem_model = None
        queries_executed_for_model = 0
        num_processed = 0

        for (model_id, query_id, query_text, content_id, abstract_text, q_upd, c_upd) in filtered_queue:

            # Se il modello attivo non corrisponde o abbiamo raggiunto il limite di query per modello,
            # verifichiamo lo stato corrente tramite /status e, se necessario, cambiamo modello.
            if current_onprem_model != model_id or queries_executed_for_model >= MAX_QUERIES_PER_MODEL:
                status_info = get_onprem_status()
                if not status_info or status_info.get("current_model") != model_id:
                    logger.info(f"🔄 Cambio modello in corso: set_onprem_model_and_wait({model_id})")
                    set_onprem_model_and_wait(model_id)
                    status_info = get_onprem_status()
                    current_onprem_model = status_info.get("current_model") if status_info else None
                    queries_executed_for_model = 0
                else:
                    current_onprem_model = status_info.get("current_model")
                    queries_executed_for_model = 0

            response = send_to_onprem_llm(query_text, abstract_text, model_id)
            if response and response != "❌ Nessun modello caricato.":
                save_result_to_couchdb(query_id, content_id, response, q_upd, c_upd, model_id)
                num_processed += 1
            queries_executed_for_model += 1

        logger.info(f"🟢 {num_processed} nuove query processate.")

    except Exception as e:
        logger.error(f"❌ Errore nel ciclo di elaborazione: {e}")


def get_onprem_status(timeout=10):
    """
    Recupera lo stato corrente di OnPremLLM, che include:
      - "status": "ok" se il modello è caricato, altrimenti "loading"
      - "current_model": il modello attualmente attivo (quando status è "ok")
      - "loading_model": il modello in fase di caricamento (quando status è "loading")
    """
    url_status = "http://onprem:5001/status"
    try:
        resp = requests.get(url_status, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.warning(f"⚠️ /status ha ritornato codice {resp.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"⚠️ Errore chiamando /status: {e}")
        return None


def process_changes():
    """
    Carica l'intero contenuto dei database da CouchDB e aggiorna i DataFrame Spark.
    Le tabelle temporanee vengono create con tutti i documenti, così che le query
    vengano eseguite se non sono presenti in changes_couchdb_documents_paperllm_results.
    """
    schemas = {
        "paperllm_content": "`_id` STRING, `title` STRING, `abstract` STRING, `updated_at` STRING",
        "paperllm_query": "`_id` STRING, `text` STRING, `updated_at` STRING",
        "paperllm_results": "`_id` STRING, `query_id` STRING, `content_id` STRING, `response` STRING, `query_updated_at` STRING, `content_updated_at` STRING, `model_id` STRING"
    }

    # Per ciascun database, recuperiamo tutti i documenti partendo da "0"
    for db_name in schemas.keys():
        valid_changes, _ = get_changes_from_couchdb(db_name, "0")
        if valid_changes:
            documents = [change['doc'] for change in valid_changes if 'doc' in change]
            df = spark.createDataFrame(documents)
        else:
            df = spark.createDataFrame([], schema=schemas[db_name])
        df.createOrReplaceTempView(f"changes_couchdb_documents_{db_name}")
        logger.info(f"Tabella 'changes_couchdb_documents_{db_name}' aggiornata con {len(valid_changes)} documenti.")


# Main loop
while True:
    try:
        logger.info("🟢 1. Aggiornamento dati da CouchDB in Spark...")
        process_changes()

        logger.info("🔵 2. Elaborazione delle query con OnPremLLM...")
        process_queries_with_abstracts()

    except Exception as e:
        logger.error(f"❌ Errore nel ciclo di elaborazione: {e}")

    logger.info("⏳ Attesa 60 secondi per il prossimo ciclo...")
    time.sleep(60)
