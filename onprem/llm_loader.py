import logging
from onprem import LLM
from config import get_model_by_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = None  # Modello attualmente in memoria

def load_model(model_id):
    """
    Carica dinamicamente il modello specificato.
    """
    global llm
    model = get_model_by_id(model_id)

    if llm:
        del llm  # Rilascia memoria del modello precedente

    logger.info(f"🚀 Caricamento del modello {model_id}...")
    llm = LLM(
        model_download_path=model["path"],
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
        verbose=True
    )
    logger.info(f"✅ Modello {model_id} caricato con successo.")

def process_with_llm(prompt):
    """
    Esegue l'inferenza con il modello caricato.
    """
    global llm
    if not llm:
        return "❌ Nessun modello caricato."

    return llm.prompt(prompt)