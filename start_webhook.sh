#!/bin/bash

# 创建日志目录
mkdir -p logs

start_webhook() {
    echo "Starting webhook service..."
    python3 alert_webhook.py > logs/webhook.log 2>&1 &
    
    # 保存PID
    echo $! > webhook.pid
    echo "Webhook service started with PID $(cat webhook.pid)"
}

stop_webhook() {
    if [ -f webhook.pid ]; then
        echo "Stopping webhook service..."
        kill $(cat webhook.pid)
        rm webhook.pids
        echo "Webhook service stopped"
    else
        echo "Webhook service is not running"
    fi
}

restart_webhook() {
    stop_webhook
    sleep 2
    start_webhook
}

case "$1" in
    start)
        start_webhook
        ;;
    stop)
        stop_webhook
        ;;
    restart)
        restart_webhook
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0 