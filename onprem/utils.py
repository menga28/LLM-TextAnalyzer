import os
import logging
import hashlib
import requests
from tqdm import tqdm
from config import MODELS, MODEL_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def calculate_sha256(file_path: str, hash_algo='sha256'):
    """Calculates the SHA256 hash of a file."""
    logger.info(f"Starting SHA256 calculation for file: {file_path}")

    hash_func = hashlib.new(hash_algo)
    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        sha256_hash = hash_func.hexdigest()
        logger.info(f"SHA256 hash calculated successfully: {sha256_hash}")
        return sha256_hash
    except Exception as e:
        logger.error(f"Failed to calculate SHA256 for {file_path}: {e}")
        return None


def calculate_md5(file_path: str, hash_algo='md5'):
    """Calculates the MD5 hash of a file."""
    logger.info(f"Starting MD5 calculation for file: {file_path}")

    hash_func = hashlib.new(hash_algo)
    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        md5_hash = hash_func.hexdigest()
        logger.info(f"MD5 hash calculated successfully: {md5_hash}")
        return md5_hash
    except Exception as e:
        logger.error(f"Failed to calculate MD5 for {file_path}: {e}")
        return None


def check_all_models():
    """Downloads all models listed in the configuration."""
    logger.info("Starting checking models process...")

    for model in MODELS:
        try:
            logger.info(f"Processing model: {model['id']} - {model['path']}")
            download_model(
                MODEL_DIR, model["path"], model["url"], model["hash_sha256"]
            )
            logger.info(
                f"✅ Model {model['id']} is available at {model['path']}")
        except Exception as e:
            logger.error(f"❌ Error downloading model {model['id']}: {e}")


def download_model(model_dir: str, model_path: str, model_url: str, expected_hash_sha256: str, min_file_size: int = 2*1024*1024*1024):
    """Handles the verification and downloading of a model."""
    logger.info(f"Checking model file: {model_path}")
    
    if os.path.exists(model_path):
        if os.path.isdir(model_path):
            logger.error(f"❌ Error: {model_path} is a directory, not a file.")
            return
        
        valid_size = os.path.getsize(model_path) >= min_file_size
        valid_hash = calculate_sha256(model_path) == expected_hash_sha256
        
        if valid_hash and valid_size:
            logger.info(f"✅ Model file exists and is valid: {model_path}")
            return
        else:
            logger.warning(f"⚠️ Model file exists but is invalid. Redownloading: {model_path}")
    else:
        logger.info(f"⬇️ Model does not exist. Starting download: {model_path}")
    
    download_and_save_model(model_url, model_path)



def download_and_save_model(model_url, model_path):
    """Downloads and saves the model from the provided URL."""
    logger.info(f"Initiating download from {model_url} to {model_path}...")

    downloaded_size = 0
    if os.path.exists(model_path):
        downloaded_size = os.path.getsize(model_path)
        logger.info(
            f"Resuming from partial file: {model_path}, size: {downloaded_size} bytes")

    response = requests.head(model_url)
    total_size = int(response.headers.get('Content-Length', 0))

    if downloaded_size >= total_size:
        logger.info(
            f"✔️ File already fully downloaded: {model_path}, size: {downloaded_size}/{total_size} bytes")
        return

    headers = {"Range": f"bytes={downloaded_size}-"}
    try:
        with requests.get(model_url, headers=headers, stream=True) as response:
            response.raise_for_status()

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

        logger.info(f"✅ Model downloaded successfully: {model_path}")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to download model {model_url}: {e}")
