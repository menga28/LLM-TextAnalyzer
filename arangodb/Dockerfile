# Utilizziamo l'immagine ufficiale di ArangoDB come base
FROM arangodb/arangodb:latest

# Copiamo eventuali configurazioni personalizzate nella directory di ArangoDB
COPY arangodb.conf /etc/arangodb3/arangod.conf

# Definiamo la porta di default e la directory di lavoro
EXPOSE 8529
WORKDIR /var/lib/arangodb3

# Lanciando ArangoDB con il file di configurazione
CMD ["arangod", "--config", "/etc/arangodb3/arangod.conf"]
