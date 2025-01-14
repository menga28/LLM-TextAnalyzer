import logging
from onprem import LLM

def start_llm():
    logging.info("Inizializzazione del servizio onprem LLM...")
    llm = LLM()
    # Qui puoi configurare o chiamare metodi di `LLM` come necessario
    response = llm.some_method("Test input")  # Esempio di metodo
    logging.info(f"Risposta da LLM: {response}")
