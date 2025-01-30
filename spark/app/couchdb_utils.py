import logging
import traceback
from couchdb import Server
import os

# Configurazione del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recupero delle variabili d'ambiente
couchdb_url = os.getenv("COUCHDB_URL")
couchdb_user = os.getenv("COUCHDB_USER")
couchdb_password = os.getenv("COUCHDB_PASSWORD")

couchdb_url_with_credentials = f"http://{couchdb_user}:{couchdb_password}@{couchdb_url}"

def get_changes_from_couchdb(db_name, since_seq):
    """
    Recupera le modifiche da CouchDB usando il feed `_changes`, escludendo i documenti eliminati.
    """
    try:
        couch_server = Server(couchdb_url_with_credentials)
        couch_db = couch_server[db_name]

        changes = couch_db.changes(since=since_seq, include_docs=True)
        
        valid_changes = [
            change for change in changes['results']
            if not change.get('deleted', False) and 'doc' in change
        ]

        if not valid_changes and since_seq == "0":
            # ✅ Se è la prima esecuzione, carichiamo tutti i documenti
            valid_changes = [{"doc": doc} for doc in couch_db.view('_all_docs', include_docs=True)]
            logger.info(f"⚠️ Nessuna modifica trovata per {db_name}, caricando tutti i documenti iniziali.")

        logger.info(f"Recuperati {len(valid_changes)} documenti dal database {db_name}.")
        return valid_changes, changes.get('last_seq', since_seq)
    except Exception as e:
        logger.error(f"Errore nel recupero dei documenti da {db_name}: {e}")
        logger.error("Dettagli dell'errore:\n" + traceback.format_exc())
        return [], since_seq

def save_result_to_couchdb(query_id, content_id, response, query_updated_at, content_updated_at):
    """
    Salva il risultato della query su CouchDB nel database 'results'.
    """
    try:
        couch_server = Server(couchdb_url_with_credentials)
        couch_db = couch_server["paperllm_results"]
        
        result_doc = {
            "_id": f"{content_id}_{query_id}",
            "query_id": query_id,
            "content_id": content_id,
            "response": response,
            "query_updated_at": query_updated_at,
            "content_updated_at": content_updated_at
        }
        
        couch_db.save(result_doc)
        logger.info(f"Risultato salvato in CouchDB: {result_doc['_id']}")
    
    except Exception as e:
        logger.error(f"Errore nel salvataggio del risultato su CouchDB: {e}")
