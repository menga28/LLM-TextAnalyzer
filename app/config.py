import os

MODEL_DIR = "/app/llm_model"
MODELS = [
    {
        "id": "mistral-7b",
        "path": os.path.join(MODEL_DIR, "mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "hash_md5": "d98804ecfe3f274b46aed70d9257945e"
    },
    {
        "id": "llama-3.2-3b",
        "path": os.path.join(MODEL_DIR, "Llama-3.2-3B-Instruct-uncensored-Q8_0.gguf"),
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-uncensored-GGUF/resolve/main/Llama-3.2-3B-Instruct-uncensored-Q8_0.gguf",
        "hash_md5": "08dd494d754c926afddc737400ab6c91"
    }
]


def get_model_by_id(model_id):
    for model in MODELS:
        if model["id"] == model_id:
            return model
    raise ValueError(f"No model found with id '{model_id}'")
