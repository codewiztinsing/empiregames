#!/bin/bash

# Check status of Celery services for Liyu Bingo

cd /home/tinsae/Desktop/projects/empiregames/app

echo "📋 Celery Services Status"
echo "========================"

# Function to check service status
check_service() {
    local service_name=$1
    local pid_file="${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "✅ $service_name: Running (PID: $pid)"
        else
            echo "❌ $service_name: Not running (stale PID file)"
        fi
    else
        echo "❌ $service_name: Not running (no PID file)"
    fi
}

# Check all services
check_service "celery-worker"
check_service "celery-beat"
check_service "celery-flower"

echo ""
echo "📊 Quick Tests:"
echo "==============="

# Test Celery connection
echo -n "Testing Celery connection... "
if python -c "from core.celery import app; print('✅ OK')" 2>/dev/null; then
    echo ""
else
    echo "❌ Failed"
fi

# Test RabbitMQ connection
echo -n "Testing RabbitMQ connection... "
if python -c "import pika; pika.BlockingConnection(pika.ConnectionParameters('localhost')); print('✅ OK')" 2>/dev/null; then
    echo ""
else
    echo "❌ Failed"
fi

echo ""
echo "🌐 Access Points:"
echo "=================="
echo "  - Celery Flower: http://localhost:5555"
echo "  - RabbitMQ Management: http://localhost:15672"
echo ""
echo "📝 Recent Logs:"
echo "==============="
echo "Worker (last 5 lines):"
tail -5 celery-worker.log 2>/dev/null || echo "  No log file found"
echo ""
echo "Beat (last 5 lines):"
tail -5 celery-beat.log 2>/dev/null || echo "  No log file found"
echo ""
echo "Flower (last 5 lines):"
tail -5 celery-flower.log 2>/dev/null || echo "  No log file found"
