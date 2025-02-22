#!/bin/bash

echo "Avvio dello script di inizializzazione..."

# Ottieni l'IP del container di CouchDB
COUCHDB_IP=$(hostname -i)

# Funzione per controllare se CouchDB è pronto
is_couchdb_ready() {
    curl -s http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/_up | grep -q '"status":"ok"'
}

# Attende fino a quando CouchDB è disponibile
echo "Attesa dell'avvio di CouchDB..."
timeout=300  # Timeout massimo in secondi
interval=10  # Intervallo di verifica
elapsed=0

while ! is_couchdb_ready; do
    if [ $elapsed -ge $timeout ]; then
        echo "Timeout raggiunto: CouchDB non è pronto."
        exit 1
    fi
    echo "CouchDB non ancora pronto. Riprovo tra $interval secondi..."
    sleep $interval
    elapsed=$((elapsed + interval))
done

echo "CouchDB è pronto!"

# Crea i database di sistema se non esistono
system_databases=("_users" "_replicator" "_global_changes")

for db in "${system_databases[@]}"; do
    echo "Creazione del database di sistema $db..."
    curl -s -X PUT http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/$db?q=1 || echo "Il database di sistema $db esiste già."
done

# Crea i database personalizzati se non esistono
custom_databases=("paperllm_content" "paperllm_query" "paperllm_results")

for db in "${custom_databases[@]}"; do
    echo "Creazione del database $db..."
    curl -s -X PUT http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/$db?q=1 || echo "Il database $db esiste già."
done

echo "Inizializzazione completata!"
