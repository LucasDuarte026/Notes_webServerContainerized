FROM opensuse/leap:15.5

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
# RUN mkdir -p /docker-entrypoint-initdb.d    
# COPY init.sql /docker-entrypoint-initdb.d/

# Switch to postgres user to perform PostgreSQL commands
USER postgres
    
#  initialize the database and start the PostgreSQL server
# RUN /usr/lib/postgresql/bin/postgres -D /var/lib/pgsql/data & \
#     until /usr/lib/postgresql/bin/pg_isready -h localhost -p 5432; do \
#         sleep 1; \
#     done && \
#     psql -U postgres -f /docker-entrypoint-initdb.d/init.sql

# RUN pg_ctl -D /var/lib/pgsql/data stop

# Expose the PostgreSQL port
EXPOSE 5432

CMD ["/usr/lib/postgresql/bin/postgres", "-D", "/var/lib/pgsql/data"]

 
