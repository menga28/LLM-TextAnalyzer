from flask import Flask, request, jsonify
from fastapi import FastAPI
import logging
from llm_loader import load_model, process_with_llm
from config import MODELS
from utils import downloading_all_models

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modello attualmente in memoria
current_model = None
model_loaded = False


@app.route('/infer', methods=['POST'])
def infer():
    global current_model

    data = request.get_json()
    model_id = data.get("model_id")
    prompt = data.get("prompt")

    if not model_id or not prompt:
        return jsonify({"error": "I campi 'model_id' e 'prompt' sono obbligatori"}), 400

    logger.info(
        f"📥 Received inference request - Model: {model_id}, Prompt: {prompt[:100]}...")

    # Carica il modello solo se non è già in memoria
    if current_model != model_id:
        global model_loaded
        logger.info(f"🔄 Cambio modello in memoria: {model_id}")
        load_model(model_id)
        current_model = model_id
        model_loaded = True

    # Esegui il prompt
    response = process_with_llm(prompt)

    return jsonify({"response": response})


@app.route('/models', methods=['GET'])
def get_models():
    """
    Returns the list of available models.
    """
    model_list = [model["id"] for model in MODELS]
    logger.info(f"📋 Available models: {model_list}")
    return jsonify({"models": model_list})


@app.route('/status', methods=['GET'])
def status():
    """
    Restituisce lo stato del servizio:
    - "ok" se il modello è caricato
    - "loading" se il modello non è ancora caricato
    """
    if model_loaded:
        return jsonify({"status": "ok", "message": "OnPremLLM è attivo e il modello è caricato"}), 200
    else:
        return jsonify({"status": "loading", "message": "OnPremLLM è in fase di caricamento"}), 503


if __name__ == "__main__":
    downloading_all_models()
    app.run(host="0.0.0.0", port=5001)
