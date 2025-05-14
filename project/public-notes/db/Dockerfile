FROM opensuse/leap:latest

# Set environment variables for PostgreSQL
# ENV POSTGRES_USER=luska026
# ENV POSTGRES_PASSWORD=123456
# ENV POSTGRES_DB=pn_database

# Install PostgreSQL server and client
RUN zypper update & zypper -n install postgresql postgresql-server postgresql-contrib

# Create the data directory and set permissions
RUN mkdir -p /var/lib/pgsql/data && \
    chown -R postgres:postgres /var/lib/pgsql/data
RUN mkdir -p /run/postgresql && \
    chown -R postgres:postgres /run/postgresql

# Initialize the PostgreSQL database cluster
USER postgres

RUN /usr/lib/postgresql/bin/initdb -D /var/lib/pgsql/data
# Switch back to root user for subsequent commands
USER root

# Copy the PostgreSQL configuration file (pg_hba.conf) to allow connections
COPY pg_hba.conf /var/lib/pgsql/data/pg_hba.conf

# Expose the PostgreSQL port
EXPOSE 5432

USER postgres
CMD ["/usr/lib/postgresql/bin/postgres", "-D", "/var/lib/pgsql/data"]