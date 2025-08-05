# https://hub.docker.com/_/postgres
FROM postgres:17

COPY --chown=postgres docker-entrypoint-initdb.d /docker-entrypoint-initdb.d
COPY --chown=postgres postgresql.conf /etc/postgresql/postgresql.conf
RUN install -d --owner=postgres /var/log/postgres_statements
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
