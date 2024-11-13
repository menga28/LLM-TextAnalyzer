import xml.etree.ElementTree as ET
import json
import logging
import os

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

# Funzione per convertire XML di query in JSON e salvare automaticamente il JSON
def query_xml_to_json(xml_file_path):
    try:
        # Leggi il contenuto del file XML
        with open(xml_file_path, 'r') as xml_file:
            xml_data = xml_file.read()

        # Parsing dell'XML
        root = ET.fromstring(xml_data)

        # Creazione della lista per i risultati JSON
        json_outputs = []

        for question in root.find('questions').findall('question'):
            question_dict = {
                "id": question.find('id').text,
                "text": question.find('text').text
            }
            json_output = {
                "xml": {
                    "question": {
                        "question": [question_dict]
                    }
                }
            }
            json_outputs.append(json_output)

        # Salvataggio del JSON in un file
        save_json_to_file(json_outputs, xml_file_path)

        return json_outputs

    except Exception as e:
        logging.error(f"Errore nella conversione: {e}")
        return None

# Funzione per convertire XML di content in JSON e salvare automaticamente il JSON
def content_xml_to_json(xml_file_path):
    try:
        # Leggi il contenuto del file XML
        with open(xml_file_path, 'r') as content_file:
            content_data = content_file.read()

        # Parsing dell'XML
        root = ET.fromstring(content_data)

        # Creazione della lista per i risultati JSON
        json_outputs = []

        for item in root.find('search').find('items').findall('item'):
            item_dict = {
                "uuid": item.find('uuid').text,
                "title": item.find('title').text,
                "abstract": item.find('abstract').text
            }
            json_output = {
                "xml": {
                    "item": item_dict  # Ogni oggetto è un singolo item
                }
            }
            json_outputs.append(json_output)

        # Salvataggio del JSON in un file
        save_json_to_file(json_outputs, xml_file_path)

        return json_outputs

    except Exception as e:
        logging.error(f"Errore nella conversione: {e}")
        return None

# Funzione per salvare il JSON in un file se diverso dal contenuto esistente
def save_json_to_file(json_data, xml_file_path):
    try:
        # Creazione del percorso per il file JSON
        json_file_path = os.path.splitext(xml_file_path)[0] + '.json'

        # Leggi il contenuto esistente del file JSON, se presente
        existing_data_str = None
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                existing_data_str = json_file.read()  # Leggi tutto il contenuto come stringa

        # Converti i nuovi dati in una stringa di oggetti separati da newline
        new_data_lines = [json.dumps(item) for item in json_data]

        # Confronta i dati esistenti con i nuovi dati da scrivere (come stringhe)
        if existing_data_str != '\n'.join(new_data_lines):
            # Scrittura del file JSON solo se i dati sono diversi
            with open(json_file_path, 'w') as json_file:
                for line in new_data_lines:
                    json_file.write(line + '\n')  # Scrivi ogni oggetto su una nuova riga

            logging.info(f"File JSON salvato con successo: {json_file_path}")
        else:
            logging.info(f"Nessuna modifica necessaria. Il contenuto di {json_file_path} è già aggiornato.")

    except Exception as e:
        logging.error(f"Errore nel salvataggio del file JSON: {e}")
