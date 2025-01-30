FROM bitnami/spark:latest

# Copia i file di configurazione di Spark
COPY spark-defaults.conf /opt/bitnami/spark/conf/

# Imposta la directory di lavoro
WORKDIR /spark

# Copia i file dell'applicazione nella directory di lavoro
COPY . /spark/
#COPY app/read_couchdb_structuredstreaming.py /spark/app/read_couchdb_structuredstreaming.py
#COPY app/readcouchdb_changesfeed.py /spark/app/readcouchdb_changesfeed.py
#COPY requirements.txt /spark/requirements.txt

# Installa le librerie Python richieste
RUN pip install --no-cache-dir -r requirements.txt

# Comando di default (da modificare se necessario)
CMD ["spark-submit", "/spark/app/spark_processes.py"]