#!/bin/bash

echo "Avvio dello script di inizializzazione..."

# Ottieni l'IP del container di CouchDB
COUCHDB_IP=$(hostname -i)

# Funzione per controllare se CouchDB è pronto
is_couchdb_ready() {
    curl -s http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/_up | grep -q '"status":"ok"'
}


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

db_exists() {
    # Esegue una GET sul database. Se trova "db_name", il database esiste.
    if curl -s -X GET http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/$1 | grep -q '"db_name"'; then
        return 0
    else
        return 1
    fi
}

# Crea i database di sistema se non esistono
system_databases=("_users" "_replicator" "_global_changes")
for db in "${system_databases[@]}"; do
    if db_exists "$db"; then
        echo "Il database di sistema $db esiste già."
    else
        echo "Creazione del database di sistema $db..."
        curl -s -X PUT http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/$db?q=1
    fi
done

# Crea i database personalizzati se non esistono
custom_databases=("paperllm_content" "paperllm_query" "paperllm_results")
for db in "${custom_databases[@]}"; do
    if db_exists "$db"; then
        echo "Il database $db esiste già."
    else
        echo "Creazione del database $db..."
        curl -s -X PUT http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_IP:5984/$db?q=1
    fi
done

echo "Inizializzazione completata!"
