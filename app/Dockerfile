# Usa un'immagine base con Python
FROM python:3.11-slim

# Installa i pacchetti necessari, ordinati alfabeticamente
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Imposta la cartella di lavoro nel container
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Crea la cartella onprem_data all'interno della cartella app
RUN mkdir -p /app/onprem_data

# Scarica il modello da Hugging Face nella cartella onprem_data
ADD https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf /app/onprem_data/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Copia il resto dei file dell'applicazione
COPY . /app/

# Mostra la struttura delle cartelle nel container
RUN echo "Visualizzo le cartelle nella directory /app:" && ls -R /app
RUN echo "Visualizzo le cartelle nella directory /:" && ls -R /

# Forza l'input del download (non richiede conferma interattiva)
RUN echo "y" | python /app/app.py

# Comando di avvio dell'applicazione (aggiunge sleep per mantenere il container in esecuzione)
CMD ["sh", "-c", "sleep 3600"]
