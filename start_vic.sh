#!/bin/bash


# Configuration
VICTORIA_BIN="./victoria-metrics-prod"  # Or the full path to your victoria-metrics binary
chmod 777 ${VICTORIA_BIN}
# Use relative path from the project root
DATA_DIR="./data/"
LOGS_DIR="./logs/"
# Create data directory if it doesn't exist
mkdir -p "${DATA_DIR}"
mkdir -p "${LOGS_DIR}"

# Start Victoria Metrics with nohup
nohup ${VICTORIA_BIN} \
  --storageDataPath="${DATA_DIR}" \
  --httpListenAddr=":8428" \
  --retentionPeriod="5y" \
  --search.disableCache=true \
  > ./logs/victoria.log 2>&1 &

echo "Victoria Metrics started in background. Check ./logs/victoria.log for output." 
