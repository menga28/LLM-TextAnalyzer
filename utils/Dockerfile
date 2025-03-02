# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

# Abilita la cache APT e installa i pacchetti necessari
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    g++ \
    gcc \
    git \
    libopenblas-openmp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /utils

# Usa il mount della cache per pip
RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --upgrade pip

# Copia solo il file requirements.txt per sfruttare la cache di Docker
COPY requirements.txt /utils/

# Installa le dipendenze con caching di pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copia il resto del codice solo dopo aver installato le dipendenze
COPY . /utils/

# Assicuriamoci che lo script sia eseguibile (se necessario)
RUN chmod +x /utils/run.py

CMD ["python", "run.py"]
