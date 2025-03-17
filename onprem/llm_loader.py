import logging
import os
from onprem import LLM
from config import get_model_by_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = None
prompt_template = None


def load_model(model_id):
    """
    Carica dinamicamente il modello specificato.
    """
    global llm, prompt_template

    model = get_model_by_id(model_id)

    if llm:
        llm = None

    logger.info(f"🚀 Caricamento del modello {model_id} da {model['path']}...")

    model_directory = os.path.dirname(model["path"])

    if not os.path.isfile(model["path"]):
        logger.error(f"❌ Il percorso non è un file valido: {model['path']}")
        return

    prompt_template = model["prompt_template"]

    llm = LLM(
        model_download_path=model_directory,
        model_url=os.path.basename(model["path"]),
        prompt_template=prompt_template,
        embedding_model_kwargs={'device': 'cpu'},
        confirm=False,
        n_gpu_layers=40,
        n_threads=8,
        temperature=0.01,
        max_tokens=300,
        stop=[],
        use_mlock=True,
        use_mmap=True,
        verbose=True,
        chat_format=None
    )

    logger.info(f"✅ Modello {model_id} caricato con successo.")
    logger.info(f"📝 Prompt template impostato globalmente: {prompt_template}")


def process_with_llm(prompt):
    """
    Esegue l'inferenza con il modello caricato.
    """
    global llm, prompt_template

    if not llm:
        return "❌ Nessun modello caricato."

    logger.info(f"📤 Prompt inviato a LLM: {prompt}")
    logger.info(f"📝 Usando il prompt template: {prompt_template}")

    response = llm.prompt(prompt, prompt_template=prompt_template)
    logger.info(f"📝 Risposta generata: {response}")

    return response
