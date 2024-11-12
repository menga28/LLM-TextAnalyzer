import os
import glob
import logging
import xml.etree.ElementTree as ET
import pandas as pd

# Configura il logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_dataframe_from_xml(file_path):
    logging.info(f'Processing file: {file_path}')
    try:
        # Leggi e analizza il file XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Estrai i dati dal file XML
        data = []
        for child in root:
            row_data = {}
            for subchild in child:
                if subchild:
                    row_data[subchild.tag] = ET.tostring(subchild, encoding='unicode', method='xml').strip()
                else:
                    row_data[subchild.tag] = subchild.text.strip() if subchild.text else ''
            data.append(row_data)

        # Crea un DataFrame dai dati estratti
        df = pd.DataFrame(data)
        logging.info(f'DataFrame for {file_path}:\n{df}')

        # Salva il DataFrame in un file CSV
        csv_file_path = os.path.splitext(file_path)[0] + '.csv'
        df.to_csv(csv_file_path, index=False)
        logging.info(f'Saved DataFrame to {csv_file_path}')
        
    except Exception as e:
        logging.error(f'Error processing file {file_path}: {e}')

def process_all_xml_files(directory_path):
    logging.info(f'Starting to process XML files in directory: {directory_path}')
    xml_files = glob.glob(os.path.join(directory_path, '*.xml'))
    logging.info(f'Found {len(xml_files)} XML files.')
    for xml_file in xml_files:
        if os.path.isfile(xml_file):
            logging.info(f'Processing file: {xml_file}')
            create_dataframe_from_xml(xml_file)
        else:
            logging.warning(f'Skipping directory: {xml_file}')
    logging.info('Finished processing all XML files.')

if __name__ == "__main__":
    directory_path = input("Inserisci il percorso della directory contenente i file XML: ")
    process_all_xml_files(directory_path)
    logging.info("Tutti i file XML sono stati processati e sovrascritti.")
