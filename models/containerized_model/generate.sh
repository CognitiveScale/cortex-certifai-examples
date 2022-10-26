#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"

function usage() {
    printf "usage: ./generate.sh [options] [args]\n"
    printf "Required:\n"
    printf "\tTarget docker image to be built                          [-i | --target-docker-image]\n"
    printf "\tCertifai Toolkit path (unzipped directory)               [-t | --toolkit-path]\n"
    printf "Optional:\n"
    printf "\tRequirements (requirements.txt) file path                [-f | --requirements-file]\n"
    printf "\tPrediction Service (prediction_service.py) file path     [-p | --prediction-service-file]\n"
    printf "\tBase docker image to be used to build the image          [-b | --base-docker-image]\n"
    printf "\tDirectory to be created                                  [-d | --dir]\n"
    printf "\tModel type for template e.g h2o_mojo                     [-m | --model-type]\n"
    printf "\tModel (.pkl) file path                                   [-l | --model]\n"
    printf "\tPrint help                                               [-h | --help]\n"
}

if [ "$1" = "" ]; then
  usage
  exit
fi

DEFAULT_DIR_NAME="generated-container-model"
DEFAULT_BASE_IMAGE="python:3.8-slim"
DEFAULT_MODEL_TYPE="python"
DEFAULT_OUTPUT_PATH="."
DEFAULT_K8S_RESOURCE_NAME="container-model"
DEFAULT_K8S_NAMESPACE="containermodel"
DEFAULT_REQUIREMENTS_FILE_PATH=""
DEFAULT_PREDITCION_SERVICE_FILEPATH=""
DEFAULT_MODEL_FILEPATH=""

DIR_NAME=""
BASE_DOCKER_IMAGE=""
MODEL_TYPE=""
OUTPUT_PATH=""
TARGET_DOCKER_IMAGE=""
K8S_RESOURCE_NAME=""
K8S_NAMESPACE=""
REQUIREMENTS_FILE_PATH=""
TOOLKIT_PATH=""
PREDICTION_SERVICE_FILEPATH=""
MODEL_FILEPATH=""

while [ "$1" != "" ]; do
    case $1 in
        -d | --dir )                                          shift
                                                              DIR_NAME="$1"
                                                              ;;
        -i | --target-docker-image )                          shift
                                                              TARGET_DOCKER_IMAGE="$1"
                                                              ;;
        -t | --toolkit-path )                                 shift
                                                              TOOLKIT_PATH="$1"
                                                              ;;
        -f | --requirements-file )                            shift
                                                              REQUIREMENTS_FILE_PATH="$1"
                                                              ;;
        -p | --prediction-service-file )                      shift
                                                              PREDICTION_SERVICE_FILEPATH="$1"
                                                              ;;
        -b | --base-docker-image )                            shift
                                                              BASE_DOCKER_IMAGE="$1"
                                                              ;;
        -m | --model-type )                                   shift
                                                              MODEL_TYPE="$1"
                                                              ;;
        -r | --k8s-resource-name )                            shift
                                                              K8S_RESOURCE_NAME="$1"
                                                              ;;
        -n | --namespace )                                    shift
                                                              K8S_NAMESPACE="$1"
                                                              ;;
        -l | --model )                                        shift
                                                              MODEL_FILEPATH="$1"
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

if [ "$TOOLKIT_PATH" = "" ]; then
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

if [ "$OUTPUT_PATH" = "" ]; then
  OUTPUT_PATH=$DEFAULT_OUTPUT_PATH
fi

if [ "$K8S_RESOURCE_NAME" = "" ]; then
  K8S_RESOURCE_NAME=$DEFAULT_K8S_RESOURCE_NAME
fi

if [ "$K8S_NAMESPACE" = "" ]; then
  K8S_NAMESPACE=$DEFAULT_K8S_NAMESPACE
fi

if [ "$REQUIREMENTS_FILE_PATH" = "" ]; then
  REQUIREMENTS_FILE_PATH=$DEFAULT_REQUIREMENTS_FILE_PATH
fi

if [ "$PREDICTION_SERVICE_FILEPATH" = "" ]; then
  PREDICTION_SERVICE_FILEPATH=$DEFAULT_PREDITCION_SERVICE_FILEPATH
fi

if [ "$MODEL_FILEPATH" = "" ]; then
  MODEL_FILEPATH=$DEFAULT_MODEL_FILEPATH
fi

echo "Generating template using following configuration:"
echo "DIR = ${DIR_NAME}"
echo "BASE DOCKER IMAGE = ${BASE_DOCKER_IMAGE}"
echo "TARGET_DOCKER_IMAGE = ${TARGET_DOCKER_IMAGE}"
echo "MODEL TYPE = ${MODEL_TYPE}"
echo "CERTIFAI_TOOLKIT_PATH = ${TOOLKIT_PATH}"
echo "REQUIREMENTS_FILE_PATH = ${REQUIREMENTS_FILE_PATH}"
echo "PREDICTION_SERVICE_FILEPATH" = ${PREDICTION_SERVICE_FILEPATH}
python $SCRIPT_PATH/template.py --dir=$DIR_NAME --target-docker-image=$TARGET_DOCKER_IMAGE --base-docker-image=$BASE_DOCKER_IMAGE --model-type=$MODEL_TYPE --k8s-resource-name=$K8S_RESOURCE_NAME --k8s-namespace=$K8S_NAMESPACE --toolkit-path=$TOOLKIT_PATH --requirements-file=$REQUIREMENTS_FILE_PATH --prediction-service-file=$PREDICTION_SERVICE_FILEPATH --model=$MODEL_FILEPATH
