#!/bin/bash

# Extract host and port from $SQL_ALCHEMY_DATABASE_URI
HOST=$(echo $SQL_ALCHEMY_DATABASE_URI | sed -e 's;.*://\([^@]*@\)\?\([^:]*\):\([0-9]*\)/.*;\2;')
PORT=$(echo $SQL_ALCHEMY_DATABASE_URI | sed -e 's;.*://\([^@]*@\)\?\([^:]*\):\([0-9]*\)/.*;\3;')


# Wait for the database to be ready
echo "Waiting for database to be ready..."
until nc -z -v $HOST $PORT
do
  echo "Waiting for database connection..."
  # wait for 0.5 seconds before checking again
  sleep 0.5
done

echo "Database is up, running migrations..."

# Run database migrations
flask db upgrade

# Migrate default masks
python masks.py

# application will run from docker-compose
exec "$@"