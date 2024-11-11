# Usa un'immagine base con Python (puoi scegliere una versione specifica se necessario)
FROM python:3.11-slim

# Imposta la cartella di lavoro nel container
WORKDIR /app

# Copia i file della cartella app (compreso app.py) nel container
COPY . /app

# Installa le dipendenze del progetto (presumendo che tu abbia un file requirements.txt)
RUN pip install -r requirements.txt

# Imposta il comando predefinito per avviare lo script Python
CMD ["python", "app.py"]
