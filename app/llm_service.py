import logging
import os
from onprem import LLM
from tqdm import tqdm
from utils import download_model
from config import get_model_by_id, MODEL_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

llm = None

def creating_llm(model):
    try:
        llm = LLM(model_download_path=model["path"],
                    prompt_template="[INST] {prompt} [/INST]",
                    confirm=False,
                    n_gpu_layers=-1,
                    temperature=0,
                    verbose=True)
        logging.info("Modello LLM inizializzato.")
    except Exception as e:
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

def downloading_all_models():
    for model in MODELS:
        try:
            download_model(MODEL_DIR, model["path"], model["url"], model["hash_md5"])
            logger.info(f"Model available at {model['path']}")
        except Exception as e:
            logger.error(f"Error downloading model: {e}")

if __name__ == "__main__":
    downloading_all_models()
    logging.info("Starting application...")