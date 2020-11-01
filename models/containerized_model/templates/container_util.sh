#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"

# Set docker image name
DOCKER_IMAGE_NAME={{TARGET_DOCKER_IMAGE}}

DEFAULT_ENVIRONMENT_FILE="$SCRIPT_PATH/environment.yml"

COMMAND=$1
if [ "$COMMAND" = "build" ]; then
  docker build -t $DOCKER_IMAGE_NAME $SCRIPT_PATH
elif [ "$COMMAND" = "run" ]; then
  ENV_PATH=$DEFAULT_ENVIRONMENT_FILE
  if [ "$2" = "-e" ] || [ "$2" = "--env" ]; then
    if [ "$3" = "" ]; then
      echo "Please specify an ABSOLUTE environment file path. Usage: -e /Users/user/environment.yml"
      exit
    fi
    ENV_PATH=$3
  fi
  echo "Reading ENV variables from $ENV_PATH"
  docker run -p 8551:8551 --env-file $ENV_PATH -it $DOCKER_IMAGE_NAME
else
  echo "Param should be one of [\"build\", \"run\"]"
fi
