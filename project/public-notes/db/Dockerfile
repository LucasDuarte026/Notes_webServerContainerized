FROM opensuse/leap:latest

# Set environment variables for PostgreSQL
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword
ENV POSTGRES_DB=mydatabase

# Install PostgreSQL server and client
RUN zypper -n install postgresql15-server postgresql15

# Create the data directory and set permissions
RUN mkdir -p /var/lib/pgsql/data
RUN chown -R postgres:postgres /var/lib/pgsql/data

# Initialize the PostgreSQL database cluster
USER postgres
RUN /usr/lib/postgresql15/bin/initdb -D /var/lib/pgsql/data

# Switch back to root user for subsequent commands
USER root

# Copy the PostgreSQL configuration file (pg_hba.conf) to allow connections
COPY pg_hba.conf /var/lib/pgsql/data/pg_hba.conf

# Expose the PostgreSQL port
EXPOSE 5432

USER postgres

# Start the PostgreSQL server, ensuring the lock file directory exists
CMD mkdir -p /run/postgresql && chown -R postgres:postgres /run/postgresql && \
    /usr/lib/postgresql15/bin/postgres -D /var/lib/pgsql/data -c listen_addresses='*' -c logging_collector=off
