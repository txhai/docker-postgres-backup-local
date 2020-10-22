#!/usr/bin/env bash
docker build -t postgres-backup-local .
docker tag postgres-backup-local:latest dockerhai/postgres-backup-local:latest
docker push dockerhai/postgres-backup-local:latest
docker rm $(docker ps -a -q)
docker rmi $(docker images | grep "^<none>" | awk "{print $3}")