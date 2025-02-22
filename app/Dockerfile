FROM python:3.11-slim

# Installiamo solo i pacchetti necessari e li rimuoviamo dopo
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        curl \
        g++ \
        gcc \
        git \
        libopenblas-openmp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamo solo requirements.txt per mantenere la cache della dipendenza
COPY requirements.txt /app/

# Aggiorniamo pip e installiamo le dipendenze in un layer separato
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamo il resto del codice solo dopo aver installato le dipendenze
COPY . /app/

# Assicuriamoci che lo script sia eseguibile (se necessario)
RUN chmod +x /app/app.py

CMD ["python", "app.py"]
