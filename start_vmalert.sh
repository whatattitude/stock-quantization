#!/bin/bash

# 创建日志目录
mkdir -p logs

start_vmalert() {
    echo "Starting vmalert..."
    ./vmalert \
        -rule=./conf/vmAlert/alerts.yml \
        -datasource.url=http://localhost:8428 \
        -notifier.url=http://localhost:9093 \
        -notifier.url=http://localhost:5000/webhook \
        -remoteWrite.url=http://localhost:8428 \
        -remoteRead.url=http://localhost:8428 \
        -external.label=cluster=cn-shanghai \
        -external.label=replica=a \
        > logs/vmalert.log 2>&1 &
    
    echo $! > vmalert.pid
    echo "vmalert started with PID $(cat vmalert.pid)"
}

stop_vmalert() {
    if [ -f vmalert.pid ]; then
        echo "Stopping vmalert..."
        kill $(cat vmalert.pid)
        rm vmalert.pid
        echo "vmalert stopped"
    else
        echo "vmalert is not running"
    fi
}

reload_rules() {
    echo "Reloading alert rules..."
    curl -XPOST http://localhost:8880/-/reload
    if [ $? -eq 0 ]; then
        echo "Rules reloaded successfully"
    else
        echo "Failed to reload rules"
    fi
}

case "$1" in
    start)
        start_vmalert
        ;;
    stop)
        stop_vmalert
        ;;
    restart)
        stop_vmalert
        sleep 2
        start_vmalert
        ;;
    reload)
        reload_rules
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|reload}"
        exit 1
        ;;
esac

exit 0
