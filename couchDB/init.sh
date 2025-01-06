#!/bin/bash

# Ottieni l'IP del container di CouchDB
COUCHDB_IP=$(hostname -i)

# Attende fino a quando CouchDB è disponibile
until curl -s -o /dev/null http://$COUCHDB_IP:5984; do
    echo "In attesa di CouchDB..."
    sleep 10
done

# Crea i database se non esistono 
databases=("paperllm_content" "paperllm_query" "paperllm_result") 

for db in "${databases[@]}"; do 
    echo "Creazione del database $db..." 
    curl -X PUT http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/$db || echo "Il database $db esiste già." 
done
