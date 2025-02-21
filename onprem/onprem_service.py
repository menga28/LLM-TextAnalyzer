from flask import Flask, request, jsonify
import logging
from llm_loader import load_model, process_with_llm
from config import MODELS

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modello attualmente in memoria
current_model = None

@app.route('/infer', methods=['POST'])
def infer():
    global current_model

    data = request.get_json()
    model_id = data.get("model_id")
    prompt = data.get("prompt")

    if not model_id or not prompt:
        return jsonify({"error": "I campi 'model_id' e 'prompt' sono obbligatori"}), 400

    # Carica il modello solo se non è già in memoria
    if current_model != model_id:
        logger.info(f"🔄 Cambio modello in memoria: {model_id}")
        load_model(model_id)
        current_model = model_id

    # Esegui il prompt
    response = process_with_llm(prompt)
    
    return jsonify({"response": response})

@app.route('/models', methods=['GET'])
def get_models():
    """
    Restituisce la lista dei modelli disponibili.
    """
    return jsonify({"models": [model["id"] for model in MODELS]})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "message": "OnPremLLM è attivo"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)