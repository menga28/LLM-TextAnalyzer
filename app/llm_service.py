import logging
import os
from onprem import LLM

os.environ["AUTO_CONFIRM"] = "true"


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
        str: La risposta generata dal modello.+aa     7
    """
    llm = LLM(model_url='https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf',
              prompt_template="<s>[INST] {prompt} [/INST]",
              confirm=False,
              n_gpu_layers=-1,
              temperature=0,
              verbose=True)
    llm.download_model(confirm=True)

    # Genera la risposta
    response = llm.prompt(prompt, prompt_template=TEMPLATE)

    return response


def input(prompt=None):
    return "y"
