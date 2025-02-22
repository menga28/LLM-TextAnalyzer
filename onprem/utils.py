import os
import logging
import hashlib
import requests
from tqdm import tqdm
from config import MODELS, MODEL_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

def calculate_md5(file_path: str, hash_algo='md5'):
    hash_func = hashlib.new(hash_algo)
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def downloading_all_models():
    for model in MODELS:
        try:
            download_model(
                MODEL_DIR, model["path"], model["url"], model["hash_md5"])
            logger.info(f"Model available at {model['path']}")
        except Exception as e:
            logger.error(f"Error downloading model: {e}")

def download_model(model_dir: str, model_path: str, model_url: str, expected_hash_md5: str, min_file_size: int = 2*1024*1024*1024):
    if os.path.exists(model_path):
        valid_size = os.path.getsize(model_path) >= min_file_size
        valid_hash = calculate_md5(model_path) == expected_hash_md5
        if valid_hash and valid_size:
            logging.info(f"Model at {model_path} already exists...")
            return
    else:
        logging.info(f"Model does not exist. Downloading...")
        download_and_save_model(model_url, model_path)

def download_and_save_model(model_url, model_path):
    logger.info(f"Downloading model from {model_url} to {model_path}...")

    downloaded_size = 0
    if os.path.exists(model_path):
        downloaded_size = os.path.getsize(model_path)
        logger.info(f"Found partial file: {model_path}, size: {downloaded_size} bytes")
    
    response = requests.head(model_url)
    total_size = int(response.headers.get('X-Linked-Size', 0))

    if downloaded_size >= total_size:
        logger.info(f"File already fully downloaded: {model_path}, model actual size {downloaded_size} of {total_size} bytes")
        return

    headers = {"Range": f"bytes={downloaded_size}-"}
    with requests.get(model_url, headers=headers, stream=True) as response:
        response.raise_for_status()
        total_remaining = int(response.headers.get('content-length', 0))
        
        with open(model_path, "ab") as model_file, tqdm(
            desc="Downloading",
            initial=downloaded_size,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            ascii=True
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                model_file.write(chunk)
                progress_bar.update(len(chunk))
    logging.info("Model downloaded successfully.")