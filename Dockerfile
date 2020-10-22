ARG BASETAG=alpine
FROM postgres:$BASETAG

RUN set -x \
	&& apk update && apk add python3 bash \
	&& ln -sf python3 /usr/bin/python

RUN python -m ensurepip --upgrade \
  && pip3 install --no-cache --upgrade pip setuptools \
  && pip3 install boto3 pytz

ENV POSTGRES_DB="**None**" \
    POSTGRES_DB_FILE="**None**" \
    POSTGRES_HOST="**None**" \
    POSTGRES_PORT=5432 \
    POSTGRES_USER="**None**" \
    POSTGRES_USER_FILE="**None**" \
    POSTGRES_PASSWORD="**None**" \
    POSTGRES_PASSWORD_FILE="**None**" \
    POSTGRES_PASSFILE_STORE="**None**" \
    POSTGRES_EXTRA_OPTS="-Z9" \
    POSTGRES_CLUSTER="FALSE" \
    SCHEDULE="@daily" \
    BACKUP_DIR="/backups" \
    BACKUP_SUFFIX=".sql.gz" \
    BACKUP_KEEP_DAYS=7 \
    BACKUP_KEEP_WEEKS=4 \
    BACKUP_KEEP_MONTHS=6 \
    HEALTHCHECK_PORT=8080

COPY ./scripts/go-cron-linux-amd64-static /usr/local/bin/go-cron
COPY ./scripts/backup.sh /backup.sh
COPY ./scripts/upload.py /upload.py

RUN chmod a+x /usr/local/bin/go-cron

VOLUME /backups

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["exec /usr/local/bin/go-cron -s \"$SCHEDULE\" -p \"$HEALTHCHECK_PORT\" -- /backup.sh"]

HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f "http://localhost:$HEALTHCHECK_PORT/" || exit 1
