import xml.etree.ElementTree as ET
import json
import logging
import csv
import os
import threading
import requests
from tqdm import tqdm
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

path_xml_dataset = "/datasets/"

def calculate_md5(file_path, hash_algo='md5'):
    hash_func = hashlib.new(hash_algo)
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def download_model(MODEL_DIR, MODEL_PATH, MODEL_URL, EXPECTED_HASH_MD5, MIN_FILE_SIZE):
    logging.info(f"Checking existence of: {MODEL_PATH}")
    logging.info(f"Full absolute path: {os.path.abspath(MODEL_PATH)}")
    logging.info(f"Contents of directory: {os.listdir(MODEL_DIR)}")

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) >= MIN_FILE_SIZE:
        current_hash = calculate_md5(MODEL_PATH)
        if current_hash == EXPECTED_HASH_MD5:
            logging.info(f"Model already exists and is valid ({os.path.getsize(MODEL_PATH)} bytes). No need to download.")
        else:
            logging.warning(f"Model exists, but hash mismatch. Downloading again.")
            download_and_save_model(MODEL_URL, MODEL_PATH)
    else:
        logging.info(f"Model does not exist or is invalid. Downloading model from {MODEL_URL}...")
        download_and_save_model(MODEL_URL, MODEL_PATH)

def download_and_save_model(MODEL_URL, MODEL_PATH):
    logger.info(f"Downloading model from {MODEL_URL} to {MODEL_PATH}...")

    downloaded_size = 0
    if os.path.exists(MODEL_PATH):
        downloaded_size = os.path.getsize(MODEL_PATH)
        logger.info(f"Found partial file: {MODEL_PATH}, size: {downloaded_size} bytes")
    
    response = requests.head(MODEL_URL)
    #logger.info(f"Response headers: {response.headers}\n\n")
    total_size = int(response.headers.get('X-Linked-Size', 0))

    if downloaded_size >= total_size:
        logger.info(f"File already fully downloaded: {MODEL_PATH}, model actual size {downloaded_size} of {total_size} bytes")
        return

    headers = {"Range": f"bytes={downloaded_size}-"}
    with requests.get(MODEL_URL, headers=headers, stream=True) as response:
        response.raise_for_status()
        total_remaining = int(response.headers.get('content-length', 0))
        
        with open(MODEL_PATH, "ab") as model_file, tqdm(
            desc="Downloading",
            initial=downloaded_size,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            ascii=True
        ) as progress_bar:
            i = 0
            for chunk in response.iter_content(chunk_size=8192):
                model_file.write(chunk)
                progress = progress_bar.update(len(chunk))
                if progress is not None and progress != 0 and i > 2500:
                    logger.info(progress_bar.update(len(chunk)))
                    i = 0
                else:
                    i += 1 
    logging.info("Model downloaded successfully.")


def result_xml_to_csv(xml_file):
    logging.info(f"Converting {xml_file} to CSV")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    csv_file = xml_file.replace('.xml', '.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
        #csvwriter = csv.writer(csvfile)
        
        # Write CSV header
        csvwriter.writerow(['content_id', 'answer_id', 'text'])
        
        for result in root.findall('.//result'):
            content_id = result.get('content_id')
            for answer in result.findall('.//answer'):
                answer_id = answer.get('id')
                text = ' '.join(answer.find('text').text.split())
                csvwriter.writerow([content_id, answer_id, text])
    
    logging.info(f"CSV file created: {csv_file}")

def query_xml_to_csv(xml_file):
    logging.info(f"Converting {xml_file} to CSV")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    csv_file = xml_file.replace('.xml', '.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
        #csvwriter = csv.writer(csvfile)
        
        # Write CSV header
        csvwriter.writerow(['id', 'text'])
        
        for question in root.findall('.//question'):
            question_id = question.find('id').text
            text = question.find('text').text.strip()
            csvwriter.writerow([question_id, text])
    
    logging.info(f"CSV file created: {csv_file}")

def content_xml_to_csv(xml_file):
    logging.info(f"Converting {xml_file} to CSV")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    csv_file = xml_file.replace('.xml', '.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
        #csvwriter = csv.writer(csvfile)
        
        # Write CSV header
        csvwriter.writerow(['uuid', 'title', 'abstract'])
        
        for item in root.findall('.//item'):
            uuid = item.find('uuid').text
            title = ' '.join(item.find('title').text.split())
            abstract = ' '.join(item.find('abstract').text.split())
            csvwriter.writerow([uuid, title, abstract])
    
    logging.info(f"CSV file created: {csv_file}")