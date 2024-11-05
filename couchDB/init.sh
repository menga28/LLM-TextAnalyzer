#!/bin/bash

# Ottieni l'IP del container di CouchDB
COUCHDB_IP=$(hostname -i)

# Attende fino a quando CouchDB è disponibile
until curl -s -o /dev/null http://$COUCHDB_IP:5984; do
    echo "In attesa di CouchDB..."
    sleep 10
done

# Crea il database _users se non esiste
echo "Creazione del database _users..."
curl -X PUT http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/_users || echo "Il database _users esiste già."
