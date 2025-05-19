#!/bin/bash
set -e

# Check if the database cluster is initialized
if [ ! -f /var/lib/pgsql/data/PG_VERSION ]; then
    echo "Initializing PostgreSQL database cluster..."
    rm -rf /var/lib/pgsql/data
    /usr/lib/postgresql/bin/initdb -D /var/lib/pgsql/data

    echo "Starting temporary PostgreSQL server..."
    /usr/lib/postgresql/bin/pg_ctl -D /var/lib/pgsql/data -o "-c listen_addresses=''" -w start

    echo "Running initialization script..."
    if [ -f /docker-entrypoint-initdb.d/init.sql ]; then
        psql -U postgres -f /docker-entrypoint-initdb.d/init.sql
    fi

    echo "Stopping temporary server..."
    /usr/lib/postgresql/bin/pg_ctl -D /var/lib/pgsql/data -m fast stop
else
    echo "Database cluster already initialized."
fi

echo "Starting PostgreSQL server..."
exec /usr/lib/postgresql/bin/postgres -D /var/lib/pgsql/data
