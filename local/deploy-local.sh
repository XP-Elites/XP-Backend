#!/bin/bash

# Network name
NETWORK_NAME="xp-local-network"

# Create network if it doesn't exist
docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 || \
  docker network create "$NETWORK_NAME"

image_name="xp-webserver"
./build.sh "$image_name"
docker rm -f xp-webserver-local 2>/dev/null || true

docker run \
  -p 8000:8000 \
  -v ~/.aws:/home/appuser/.aws:ro \
  -v webserver:/storage \
  --name "xp-webserver-local" \
  --network "$NETWORK_NAME" \
  -d \
  "$image_name"




