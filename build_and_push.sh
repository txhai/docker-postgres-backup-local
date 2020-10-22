#!/usr/bin/env bash
docker build -t postgres_backup .
docker tag postgres_backup:latest dockerhai/postgres-backup-local:latest
docker push dockerhai/postgres-backup-local:latest
docker rm $(docker ps -a -q)
docker rmi $(docker images | grep "^<none>" | awk "{print $3}")