FROM couchdb:latest

# Copia lo script di inizializzazione
COPY init.sh /usr/local/bin/init.sh
RUN chmod +x /usr/local/bin/init.sh

# Avvia CouchDB e poi esegue lo script di inizializzazione
CMD ["sh", "-c", "/usr/local/bin/docker-entrypoint.sh couchdb & sleep 10 && /usr/local/bin/init.sh"]
