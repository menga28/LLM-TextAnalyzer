FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN python -m pip install --upgrade pip && pip install --use-feature=fast-deps -r requirements.txt

RUN mkdir -p /app/model

RUN if [ ! -f /app/model/mistral-7b-instruct-v0.2.Q4_K_M.gguf ]; then \ 
    curl -o /app/model/mistral-7b-instruct-v0.2.Q4_K_M.gguf https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf; \ 
    else \ echo "Model already exists"; \ 
    fi

COPY . /app/

CMD ["python", "app.py"]