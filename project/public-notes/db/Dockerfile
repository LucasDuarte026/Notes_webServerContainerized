FROM opensuse/leap:15.5

# Install PostgreSQL server and client
RUN zypper -n update && zypper -n install -y postgresql postgresql-server postgresql-contrib

# Create the data directory and set permissions

RUN mkdir -p /var/lib/pgsql/data /run/postgresql /docker-entrypoint-initdb.d && \
    chown -R postgres:postgres /var/lib/pgsql /run/postgresql /docker-entrypoint-initdb.d

    
COPY pg_hba.conf /var/lib/pgsql/data/pg_hba.conf
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

COPY init.sql /docker-entrypoint-initdb.d/init.sql
RUN chmod +x /docker-entrypoint-initdb.d/init.sql

USER postgres

EXPOSE 5432

CMD ["/usr/local/bin/docker-entrypoint.sh"]
