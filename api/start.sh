#!/bin/sh
set -e

echo "🚀 Starting API service..."

# Wait for database to be ready
echo "⏳ Waiting for database at $POSTGRES_HOST:$POSTGRES_PORT..."
until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  echo "Database is not ready yet. Retrying in 2s..."
  sleep 2
done

echo "⚠️ Resetting database..."
npx prisma migrate reset --force

echo "🎉 Database reset complete. Starting application..."
exec npm start
