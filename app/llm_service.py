import logging
import os
from onprem import LLM
from utils import download_model, downloading_all_models
from config import MODEL_DIR, MODELS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

llm = None

def creating_llm(model):
    global llm
    try:
        download_model(MODEL_DIR, model["path"],
                       model["url"], model["hash_md5"], 10000)
        absolute_path = os.path.abspath(model["path"])
        logger.info(f"Passing model_download_path: {absolute_path}")
        logger.info(f"Model available at {absolute_path}")
        logger.info(f"Using prompt template: {model['prompt_template']}")
        llm = LLM(
            model_download_path=MODEL_DIR,
            model_url=model["filename"],
            prompt_template=model["prompt_template"],
            embedding_model_kwargs={'device': 'cpu'},
            confirm=False,
            n_gpu_layers=40,
            n_threads=8,
            temperature=0.01,
            max_tokens=300,
            stop=["\n"],
            use_mlock=True,
            use_mmap=True,
            verbose=True)
        logging.info("Modello LLM inizializzato.")
    except Exception as e:
        logging.error(f"Informazioni attuali del modello: {model}")
        logging.error(f"Errore durante l'inizializzazione del modello: {e}")

def process_with_llm(prompt):
    logging.info("Inizio dell'elaborazione del prompt...")
    if llm is None:
        logging.error("Il modello non è stato inizializzato.")
        return None
    try:
        logging.info("Esecuzione del prompt...")
        response = llm.prompt(prompt)
        logging.info("Prompt eseguito con successo.")
        return response
    except Exception as e:
        logging.error(f"Errore durante l'elaborazione del prompt: {e}")
        return None

if __name__ == "__main__":
    downloading_all_models()
    logging.info("Starting Onprem Service...")