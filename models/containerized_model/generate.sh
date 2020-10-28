#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash

function usage() {
    echo "usage: ./generate.sh [options] [args]"
    echo "Required:"
    echo "\tTarget docker image to be built                      [-i | --target-docker-image]"
    echo "Optional:"
    echo "\tBase docker image to be used to build the image      [-b | --base-docker-image]"
    echo "\tDirectory to be created                              [-d | --dir]"
    echo "\tModel type for template e.g h2o_mojo                 [-m | --model-type]"
    echo "\tPrint help                                           [-h | --help]"
}

if [ "$1" = "" ]; then
  usage
  exit
fi

DEFAULT_DIR_NAME="generated-container-model"
DEFAULT_BASE_IMAGE="continuumio/miniconda3:4.7.10"
DEFAULT_MODEL_TYPE="python"
TARGET_DOCKER_IMAGE=""

DIR_NAME=""
BASE_DOCKER_IMAGE=""
MODEL_TYPE=""


while [ "$1" != "" ]; do
    case $1 in
        -d | --dir )                                          shift
                                                              DIR_NAME="$1"
                                                              ;;
        -i | --target-docker-image )                          shift
                                                              TARGET_DOCKER_IMAGE="$1"
                                                              ;;
        -b | --base-docker-image )                            shift
                                                              BASE_DOCKER_IMAGE="$1"
                                                              ;;
        -m | --model-type )                                   shift
                                                              MODEL_TYPE="$1"
                                                              ;;
        -h | --help )                                         usage
                                                              exit
                                                              ;;
        * )                                                   usage
                                                              exit 1
    esac
    shift
done

# Required params
if [ "$TARGET_DOCKER_IMAGE" = "" ]; then
  usage
  exit
fi

# Optional params
if [ "$DIR_NAME" = "" ]; then
  DIR_NAME=$DEFAULT_DIR_NAME
fi

if [ "$BASE_DOCKER_IMAGE" = "" ]; then
  BASE_DOCKER_IMAGE=$DEFAULT_BASE_IMAGE
fi

if [ "$MODEL_TYPE" = "" ]; then
  MODEL_TYPE=$DEFAULT_MODEL_TYPE
fi

echo "Generating template using following configuration:"
echo "DIR = ${DIR_NAME}"
echo "BASE DOCKER IMAGE = ${BASE_DOCKER_IMAGE}"
echo "TARGET_DOCKER_IMAGE = ${TARGET_DOCKER_IMAGE}"
echo "MODEL TYPE = ${MODEL_TYPE}"
python template.py --dir=$DIR_NAME --target-docker-image=$TARGET_DOCKER_IMAGE --base-docker-image=$BASE_DOCKER_IMAGE --model-type=$MODEL_TYPE
