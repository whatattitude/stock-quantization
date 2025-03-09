#!/bin/bash
# http://106.15.39.159:8428/vmui/?#/?g0.range_input=30m&g0.end_input=2025-03-09T07%3A38%3A40&g0.relative_time=last_30_minutes&g0.tab=0&g0.expr=%7B__name__%21%3D%22%22%7D

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
