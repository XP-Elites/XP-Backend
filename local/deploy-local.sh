#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PREFIX="xp-local"
NETWORK_NAME="$PREFIX-network"
POSTGRES_CONTAINER="$PREFIX-postgres"
RABBITMQ_CONTAINER="$PREFIX-rabbitmq"
WEBSERVER_CONTAINER="xp-webserver-local"
WORKER_CONTAINER="xp-scripts"

docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 || docker network create "$NETWORK_NAME"

docker run -d \
  --name "$POSTGRES_CONTAINER" \
  --network "$NETWORK_NAME" \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=appdb \
  -v ./init.sql:/docker-entrypoint-initdb.d/01-init.sql \
  -v $PREFIX-pgdata:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18.1

docker run -d \
  --name "$RABBITMQ_CONTAINER" \
  --network "$NETWORK_NAME" \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  -e RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS="-rabbit loopback_users []" \
  -v $PREFIX-rabbitmq-data:/var/lib/rabbitmq \
  -p 15672:15672 \
  -p 5672:5672 \
  rabbitmq:3-management

for _ in $(seq 1 30); do
  docker exec "$POSTGRES_CONTAINER" pg_isready -U admin -d appdb >/dev/null 2>&1 && break
  sleep 2
done

for _ in $(seq 1 30); do
  docker exec "$RABBITMQ_CONTAINER" rabbitmq-diagnostics -q ping >/dev/null 2>&1 && break
  sleep 2
done

./build.sh xp-webserver
docker build .. -t xp-worker:latest -f ./WorkerDockerfile

docker run -d \
  -p 8000:8000 \
  -e APP_VERSION=0.0.0-local \
  --user root \
  -v ~/.aws:/home/appuser/.aws:ro \
  -v webserver:/storage \
  --name "$WEBSERVER_CONTAINER" \
  --network "$NETWORK_NAME" \
  xp-webserver

docker run -d \
  --name "$WORKER_CONTAINER" \
  --network "$NETWORK_NAME" \
  -v webserver:/storage \
  xp-worker

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E 'NAMES|xp-local-postgres|xp-local-rabbitmq|xp-webserver-local|xp-scripts'
