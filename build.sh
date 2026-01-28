#!/bin/bash

function outputUsage {
  echo "Usage: build <image_name> [build_id]
build_id The build ID that the image is allocated
image_name The full image name, for example justcatto/fyp-api.
  "
}

image_name="${1}"
build_id="${2}"
if [[ ${#} -lt 1 ]]; then
  outputUsage
  exit 1
fi

docker build . -t "${image_name}":latest
if [[ ${#} -eq 2 ]]; then
  docker image tag "${image_name}":latest "${image_name}":"${build_id}"
fi

exit 0
