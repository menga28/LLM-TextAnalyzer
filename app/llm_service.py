import logging
from onprem import LLM

# Configura l'URL del modello LLM
MODEL_URL = "/app/onprem_data/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# Template per il prompt
TEMPLATE = """
Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{prompt}

### Response:"""

def process_with_llm(prompt):
    """
    Processa un prompt utilizzando il modello LLM.
    
    Args:
        prompt (str): Il prompt da inviare al modello.
    
    Returns:
        str: La risposta generata dal modello.
    """
    # Inizializza il modello
    llm = LLM(MODEL_URL, n_gpu_layers=-1)
    
    # Genera la risposta
    response = llm.prompt(prompt, prompt_template=TEMPLATE)
    
    return response