#!/bin/bash

# Start Django backend
echo "Starting Django backend..."
cd ..
source venv/bin/activate
cd app

python manage.py runserver &

# Wait a few seconds for Django to start
sleep 3

# Start React frontend
echo "Starting React frontend..."
cd ../bingo
npm start
nodemon server.js



# Trap SIGINT (Ctrl+C) to kill both processes
trap 'kill $(jobs -p)' SIGINT

# Wait for all background processes to complete
wait
