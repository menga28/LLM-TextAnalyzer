FROM couchdb:latest

# Copia lo script di inizializzazione
COPY init.sh /usr/local/bin/init.sh
RUN chmod +x /usr/local/bin/init.sh

# Comando per eseguire lo script all'avvio
CMD ["bash", "/usr/local/bin/init.sh"]
