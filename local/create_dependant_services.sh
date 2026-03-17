#!/bin/bash

PREFIX="xp-local"

# Network name
NETWORK_NAME="$PREFIX-network"

# Create network if it doesn't exist
docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 || \
  docker network create "$NETWORK_NAME" -d host

# Deploy Postgres
POSTGRES_CONTAINER="$PREFIX-postgres"
docker rm -f "$POSTGRES_CONTAINER" 2>/dev/null || true

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

# Deploy RabbitMQ with management UI
RABBITMQ_CONTAINER="$PREFIX-rabbitmq"
docker rm -f "$RABBITMQ_CONTAINER" 2>/dev/null || true

docker run -d \
  --name "$RABBITMQ_CONTAINER" \
  --network "$NETWORK_NAME" \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  -v $PREFIX-rabbitmq-data:/var/lib/rabbitmq \
  -p 15672:15672 \
  -p 5672:5672 \
  rabbitmq:3-management

echo "RabbitMQ and Postgres are running on network $NETWORK_NAME"
echo "RabbitMQ management UI: http://localhost:15672"
echo "Postgres default user: admin, password: secret, database: appdb"
