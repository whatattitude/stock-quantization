#!/bin/bash

# 创建日志目录
mkdir -p logs

start_cron() {
    echo "Starting stock monitoring service..."
    python cronGetter.py > logs/cron.log 2>&1 &
    
    # 保存PID
    echo $! > cron.pid
    echo "Stock monitoring service started with PID $(cat cron.pid)"
}

stop_cron() {
    if [ -f cron.pid ]; then
        echo "Stopping stock monitoring service..."
        kill $(cat cron.pid)
        rm cron.pid
        echo "Stock monitoring service stopped"
    else
        echo "Stock monitoring service is not running"
    fi
}

restart_cron() {
    stop_cron
    sleep 2
    start_cron
}

case "$1" in
    start)
        start_cron
        ;;
    stop)
        stop_cron
        ;;
    restart)
        restart_cron
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0 