import os
import xml.etree.ElementTree as ET
import logging

# Configura il logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def minify_query_xml(file_path):
    logging.info(f'Processing file: {file_path}')
    try:
        # Leggi e analizza il file XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Lista per memorizzare i nuovi XML
        new_xml_list = []

        # Estrai i dati dal file XML e crea nuovi XML
        for question in root.findall('.//question'):
            new_root = ET.Element('xml')
            new_question = ET.SubElement(new_root, 'question')
            new_question.append(question)
            new_xml_list.append(ET.tostring(new_root, encoding='unicode', method='xml'))

        # Scrivi i nuovi XML nel file
        with open(file_path, 'w', encoding='utf-8') as file:
            for new_xml in new_xml_list:
                file.write(new_xml + '\n')

        logging.info(f'Successfully processed and saved the XML file: {file_path}')

    except Exception as e:
        logging.error(f'Error processing file {file_path}: {e}')
