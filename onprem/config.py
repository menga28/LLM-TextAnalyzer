import os

MODEL_DIR = "/datasets/llm_model"
ACTUAL_MODEL = "DeepSeek-R1-8B"

# System prompt comune per Mistral e Llama
COMMON_SYSTEM_PROMPT = """You are an AI model designed to answer questions based on academic papers. You have access to the title, abstract, and a specific question related to the paper. Your task is to provide an answer that is focused and directly related to the content of the paper. Make sure to:
- Base your response only on the title and abstract of the paper.
- Answer the question as specifically as possible.
- If the question cannot be answered with the given information, politely indicate that the answer is unclear based on the provided content."""

MODELS = [
    {
        "id": "mistral-7b",
        "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "path": os.path.join(MODEL_DIR, "mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "hash_sha256": "3e0039fd0273fcbebb49228943b17831aadd55cbcbf56f0af00499be2040ccf9",
        "prompt_template": f"""[INST] {COMMON_SYSTEM_PROMPT}\n{{prompt}} [/INST]"""
    },
    {
        "id": "llama-3.2-3b",
        "filename": "Llama-3.2-3B-Instruct-uncensored-Q8_0.gguf",
        "path": os.path.join(MODEL_DIR, "Llama-3.2-3B-Instruct-uncensored-Q8_0.gguf"),
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-uncensored-GGUF/resolve/main/Llama-3.2-3B-Instruct-uncensored-Q8_0.gguf",
        "hash_sha256": "4252d3b5b2a63ff31b515585b6f01a089b71c93ab3ac3108163a612b544d5cfb",
        "prompt_template": (
            "<|begin_of_text|>"
            "<|start_header_id|>system<|end_header_id|>\n\n"
            f"{COMMON_SYSTEM_PROMPT}<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\n"
            "{prompt}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
    },
    {
        "id": "DeepSeek-R1-8B",
        "filename": "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
        "path": os.path.join(MODEL_DIR, "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf"),
        "url": "https://huggingface.co/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
        "hash_sha256": "f8eba201522ab44b79bc54166126bfaf836111ff4cbf2d13c59c3b57da10573b",
        "prompt_template": """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                            You are a concise assistant. Provide only the direct answer to the question, without explanations, reasoning, or additional context.
                            <|eot_id|><|start_header_id|>user<|end_header_id|>
                            {prompt}
                            <|eot_id|><|start_header_id|>assistant<|end_header_id|>
                            """
    }
]

def get_model_by_id(model_id):
    for model in MODELS:
        if model["id"] == model_id:
            return model
    raise ValueError(f"No model found with id '{model_id}'")