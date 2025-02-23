# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

# Abilita la cache di apt e installa solo i pacchetti necessari
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

WORKDIR /onprem

# Usa il mount della cache per pip
RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --upgrade pip

# Copia solo il file dei requisiti per sfruttare la cache di Docker
COPY requirements.txt /onprem/

# Installa i pacchetti con caching di pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copia il resto del codice solo dopo aver installato le dipendenze
COPY . /onprem/

# Assicuriamoci che lo script sia eseguibile (se necessario)
RUN chmod +x /onprem/onprem_service.py

CMD ["python", "onprem_service.py"]
