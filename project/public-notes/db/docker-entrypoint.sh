#!/bin/bash
set -e

DATA_DIR="/var/lib/pgsql/data"  # PostgreSQL data directory

# append_hba function to add entries to pg_hba.conf
append_hba() { 
    grep -qF "$1" "$DATA_DIR/pg_hba.conf" || echo "$1" >> "$DATA_DIR/pg_hba.conf" 
}

# give ownership and permissions to the data directory
chown -R postgres:postgres "$DATA_DIR"
chmod 0700 "$DATA_DIR"

# Check if the database cluster is initialized
if [ ! -f /var/lib/pgsql/data/PG_VERSION ]; then
    echo "Initializing PostgreSQL database cluster..."
    /usr/lib/postgresql/bin/initdb -D /var/lib/pgsql/data

    echo "Starting temporary PostgreSQL server..."
    /usr/lib/postgresql/bin/pg_ctl -D /var/lib/pgsql/data -o "-c listen_addresses=''" -w start

    echo "Running initialization script..."
    if [ -f /docker-entrypoint-initdb.d/init.sql ]; then
        psql -U postgres -f /docker-entrypoint-initdb.d/init.sql
    fi

    echo "Stopping temporary server..."
    /usr/lib/postgresql/bin/pg_ctl -D /var/lib/pgsql/data -m fast stop

    # Add rules for the 'lucas' user to access 'pn_database' securely
    append_hba "host    pn_database   lucas           0.0.0.0/0               scram-sha-256"

else
    echo "Database cluster already initialized."
fi

echo "Starting PostgreSQL server..."
exec /usr/lib/postgresql/bin/postgres -D /var/lib/pgsql/data -c listen_addresses='*'
