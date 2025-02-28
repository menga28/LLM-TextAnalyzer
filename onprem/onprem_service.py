import threading
from flask import Flask, request, jsonify
from fastapi import FastAPI
import logging
from llm_loader import load_model, process_with_llm
from config import MODELS
from utils import check_all_models

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    response = process_with_llm(prompt)

    return jsonify({"response": response})

@app.route('/set_model', methods=['POST'])
def set_model():
    """
    Imposta manualmente il modello corrente in memoria.
    Esempio di utilizzo: POST /set_model?model_id=mistral-7b
    """
    global current_model, model_loaded
    model_id = request.args.get("model_id")

    if not model_id:
        return jsonify({"error": "model_id parameter is missing"}), 400

    if current_model != model_id:
        logger.info(f"🔄 Richiesta set_model: {model_id}")
        load_model(model_id)
        current_model = model_id
        model_loaded = True

    return jsonify({"message": f"Model {model_id} is now set"}), 200


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
    - "loading" se il modello è in fase di caricamento
    Include inoltre il modello attualmente caricato o in caricamento.
    """
    if model_loaded:
        return jsonify({
            "status": "ok",
            "message": "OnPremLLM è attivo e il modello è caricato",
            "current_model": current_model
        }), 200
    else:
        return jsonify({
            "status": "loading",
            "message": "OnPremLLM è in fase di caricamento",
            "loading_model": current_model 
        }), 503

if __name__ == "__main__":
    thread = threading.Thread(target=check_all_models)
    thread.start()
    app.run(host="0.0.0.0", port=5001)