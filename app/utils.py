import xml.etree.ElementTree as ET
import json
import logging
import csv
import os
import threading

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

path_xml_dataset = "/datasets/"

def result_xml_to_csv(xml_file):
    logging.info(f"Converting {xml_file} to CSV")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    csv_file = xml_file.replace('.xml', '.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        
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
        csvwriter = csv.writer(csvfile)
        
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
        csvwriter = csv.writer(csvfile)
        
        # Write CSV header
        csvwriter.writerow(['uuid', 'title', 'abstract'])
        
        for item in root.findall('.//item'):
            uuid = item.find('uuid').text
            title = ' '.join(item.find('title').text.split())
            abstract = ' '.join(item.find('abstract').text.split())
            csvwriter.writerow([uuid, title, abstract])
    
    logging.info(f"CSV file created: {csv_file}")