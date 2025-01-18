import logging
import os
import requests
from onprem import LLM
from tqdm import tqdm

os.environ["AUTO_CONFIRM"] = "true"
logging.basicConfig(filename="/logs/app.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_DIR = "/app/llm_model"
MODEL_PATH = os.path.join(MODEL_DIR, "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
MIN_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1 GB in bytes

def download_model():
    # Verifica se la directory del modello esiste, se no la crea
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    # Controlla se il modello esiste già e se la sua dimensione è sufficiente
    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) >= MIN_FILE_SIZE:
        logger.info(f"Model already exists and is valid ({os.path.getsize(MODEL_PATH)} bytes). No need to download.")
    else:
        logger.info(f"Downloading model from {MODEL_URL}...")
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        with open(MODEL_PATH, "wb") as model_file, tqdm(
            desc="Downloading",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            ascii=True
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                model_file.write(chunk)
                progress_bar.update(len(chunk))
        
        logger.info("Model downloaded successfully.")

def process_with_llm(prompt):
    llm = LLM(model_download_path=MODEL_DIR,
              prompt_template="<s>[INST] {prompt} [/INST]",
              confirm=False,
              n_gpu_layers=-1,
              temperature=0,
              verbose=True)
    response = llm.prompt(prompt)
    return response

if __name__ == "__main__":
    download_model()
    logging.info("Starting application...")