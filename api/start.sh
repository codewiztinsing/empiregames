#!/bin/sh

echo "Starting API service..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
until npx prisma db push --accept-data-loss > /dev/null 2>&1; do
  echo "Database is not ready yet. Waiting..."
  sleep 2
done


echo "⚠️ Resetting database..."
npx prisma migrate reset --force

echo "Starting application..."
exec npm start
