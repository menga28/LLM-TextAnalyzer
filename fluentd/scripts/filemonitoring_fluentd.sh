#!/bin/bash

# Directory da monitorare
MONITOR_DIR="/datasets"

# File di configurazione di Fluentd
FLUENTD_CONF="/fluentd/etc/fluent.conf"

# Comando per riavviare Fluentd
RESTART_FLUENTD="fluentd -c $FLUENTD_CONF -vv"

# Monitoraggio delle modifiche
inotifywait -m -e modify $MONITOR_DIR/*.csv | while read path _ file; do
  echo "Modifica rilevata in $file. Riavvio di Fluentd..."
  pkill -f fluentd  # Terminare il processo Fluentd corrente
  $RESTART_FLUENTD  # Riavviare Fluentd
done
