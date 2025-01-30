#!/bin/bash

# Directory da monitorare
MONITOR_DIR="/datasets"

# File di configurazione di Fluentd
#FLUENTD_CONF="/fluentd/etc/fluent.conf"

# Comando per riavviare Fluentd
#RESTART_FLUENTD="fluentd -c $FLUENTD_CONF -vv"

# Monitoraggio delle modifiche
#inotifywait -m -e modify $MONITOR_DIR/*.csv | while read path _ file; do
#  echo "Modifica rilevata in $file. Riavvio di Fluentd..."
#  pkill -f fluentd  # Terminare il processo Fluentd corrente
#  $RESTART_FLUENTD  # Riavviare Fluentd
#done

# Comando per inviare segnali a Fluentd senza riavviarlo completamente
FLUENTD_PID=$(pgrep -f "fluentd")

if [ -z "$FLUENTD_PID" ]; then
  echo "❌ Fluentd non è in esecuzione. Avvio in corso..."
  fluentd -c /fluentd/etc/fluent.conf -vv &
else
  echo "✅ Fluentd è già in esecuzione con PID $FLUENTD_PID"
fi

# Monitoraggio delle modifiche
inotifywait -m -e modify $MONITOR_DIR/*.csv | while read path _ file; do
  echo "🔄 Modifica rilevata in $file. Notifico Fluentd..."
  pkill -HUP -f fluentd  # Invia segnale per rileggere i file senza riavviare
done
