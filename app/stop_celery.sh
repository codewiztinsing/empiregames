#!/bin/bash

# Stop all Celery services for Liyu Bingo

cd /home/tinsae/Desktop/projects/empiregames/app

echo "🛑 Stopping Celery services..."

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping $service_name (PID: $pid)..."
            kill $pid
            sleep 2
            if ps -p $pid > /dev/null 2>&1; then
                echo "Force killing $service_name..."
                kill -9 $pid
            fi
            echo "$service_name stopped."
        else
            echo "$service_name was not running."
        fi
        rm -f "$pid_file"
    else
        echo "No PID file found for $service_name."
    fi
}

# Stop all services
stop_service "celery-worker"
stop_service "celery-beat"
stop_service "celery-flower"

echo ""
echo "✅ All Celery services stopped!"
echo ""
echo "📝 Log files are preserved for debugging."
