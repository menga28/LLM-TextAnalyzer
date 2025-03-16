import logging
import os
from onprem import LLM
from config import get_model_by_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = None  # Modello attualmente in memoria


def load_model(model_id):
    global llm
    model = get_model_by_id(model_id)

    if llm:
        logger.info(f"🔄 Reset del modello precedente...")
        llm = None  # Reset esplicito del modello precedente

    logger.info(f"🚀 Tentativo di caricare il modello: {model_id}")
    logger.info(f"📂 Percorso file: {model['path']}")

    if not os.path.isfile(model["path"]):
        logger.error(f"❌ Il file del modello NON ESISTE: {model['path']}")
        return

    import gc
    gc.collect()

    logger.info(f"📢 Creazione dell'istanza LLM con {model['path']}")

    try:
        # Determina dinamicamente il motore in base al nome del file
        if model["path"].endswith(".gguf"):
            logger.info(
                f"🔧 Riconosciuto modello GGUF, caricamento con LlamaCpp")
            from llama_cpp import Llama
            llm = Llama(
                model_path=model["path"],  # Passiamo direttamente il file GGUF
                n_gpu_layers=40,
                n_threads=8,
                temperature=0.01,
                max_tokens=300,
                stop=["\n"],
                use_mlock=True,
                use_mmap=True,
                verbose=True
            )
        else:
            logger.info(
                f"🔧 Riconosciuto modello Transformers, caricamento con Hugging Face")
            from transformers import pipeline
            llm = pipeline("text-generation", model=model["path"])

        logger.info(f"✅ Modello {model_id} caricato con successo!")

    except Exception as e:
        logger.error(f"❌ ERRORE nel caricamento del modello {model_id}: {e}")
        llm = None

    if llm:
        logger.info(f"🟢 Modello attualmente caricato: {model_id}")
    else:
        logger.error(
            f"❌ ERRORE: Nessun modello attivo dopo il caricamento di {model_id}!")


def process_with_llm(prompt):
    """
    Esegue l'inferenza con il modello caricato.
    """
    global llm
    if not llm:
        return "❌ Nessun modello caricato."

    return llm.prompt(prompt)
