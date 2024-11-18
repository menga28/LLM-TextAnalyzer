# Usa un'immagine Spark con Python preinstallato
FROM bitnami/spark:latest

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file dell'applicazione
COPY app/ /app/

# Installa le librerie richieste
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Comando di default (da modificare se necessario)
CMD ["spark-submit", "/app/read_couchdb.py"]
