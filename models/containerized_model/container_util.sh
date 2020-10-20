#!/usr/bin/env bash

# Set docker image name and tag
DOCKER_IMAGE_NAME=certifai-containerized-model
DOCKER_IMAGE_TAG=cloud_s3

COMMAND=$1
if [ "$COMMAND" = "build" ]; then
  docker build -t $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG .
elif [ "$COMMAND" = "run" ]; then
  docker run -p 8551:8551 --env-file environment.yml -it $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG
else
  echo "Param should be one of [\"build\", \"run\"]"
fi
