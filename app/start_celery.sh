#!/bin/bash

# Start all Celery services for Liyu Bingo
# This script starts Celery Worker, Beat, and Flower

cd /home/tinsae/Desktop/projects/empiregames/app
source venv/bin/activate

echo "🚀 Starting Celery services for Liyu Bingo..."

# Function to start a service in background
start_service() {
    local service_name=$1
    local command=$2
    local log_file=$3
    
    echo "Starting $service_name..."
    nohup $command > $log_file 2>&1 &
    local pid=$!
    echo "$service_name started with PID: $pid"
    echo $pid > "${service_name}.pid"
}

# Start Celery Worker
start_service "celery-worker" "celery -A core worker -l info --concurrency=4" "celery-worker.log"

# Start Celery Beat
start_service "celery-beat" "celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler" "celery-beat.log"

# Start Celery Flower
start_service "celery-flower" "celery -A core flower --port=5555" "celery-flower.log"

echo ""
echo "✅ All Celery services started!"
echo ""
echo "📊 Access Points:"
echo "  - Celery Flower: http://localhost:5555"
echo "  - RabbitMQ Management: http://localhost:15672"
echo ""
echo "📝 Log Files:"
echo "  - Worker: celery-worker.log"
echo "  - Beat: celery-beat.log"
echo "  - Flower: celery-flower.log"
echo ""
echo "🛑 To stop all services:"
echo "  ./stop_celery.sh"
echo ""
echo "📋 To check status:"
echo "  ./status_celery.sh"