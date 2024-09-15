#!/bin/bash
# Wait for the database to be ready
echo "Waiting for database to be ready..."
until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "Waiting for database connection..."
  # wait for 5 seconds before check again
  sleep 5
done

echo "Database is up, running migrations..."

# Run database migrations
flask db upgrade

# Migrate default masks
python masks.py

# application will run from docker-compose
exec "$@"