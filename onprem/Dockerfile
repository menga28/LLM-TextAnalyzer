FROM python:3.11-slim

# Installiamo solo i pacchetti necessari e li rimuoviamo dopo per risparmiare spazio
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    g++ \
    gcc \
    git \
    libopenblas-openmp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /onprem

# Copiamo solo il file dei requisiti per sfruttare la cache di Docker
COPY requirements.txt /onprem/

# Aggiorniamo pip e installiamo i pacchetti
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamo il resto del codice solo dopo aver installato le dipendenze
COPY . /onprem/

# Assicuriamoci che lo script sia eseguibile (se necessario)
RUN chmod +x /onprem/onprem_service.py

CMD ["python", "onprem_service.py"]
