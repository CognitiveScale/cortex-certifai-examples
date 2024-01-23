#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"

function usage() {
    printf "usage: ./config_deploy.sh resource_name namespace [options]\n"
    printf "Required:\n"
    printf "\tUnique resource name for prediction service       resource_name\n"
    printf "\tUnique k8s namespace to deploy into               namespace\n"
    printf "Optional:\n"
    printf "\tPath to deployment template                       [-t | --deployment-template]\n"
    printf "\tPath to output deployment file                    [-o | --output-file]\n"
    printf "\tPath to deployment configuration file             [-c | --config-file]\n"
    printf "\tPrint help                                        [-h | --help]\n"
}

if [ "$1" = "" ]; then
  usage
  exit
fi

DEFAULT_DEPLOYMENT_TEMPLATE="${SCRIPT_PATH}/deployment_template.yml"
DEFAULT_CONFIG_FILE="${SCRIPT_PATH}/deployment_config.yml"
DEFAULT_OUTPUT_FILE="${SCRIPT_PATH}/deployment.yml"


while [ "$1" != "" ]; do
  echo "param is $1"
    case $1 in
        -t | --deployment-template )                      shift
        echo "setting deployment"
                                                          DEPLOYMENT_TEMPLATE="${1}"
                                                          ;;
        -o | --output-file )                              shift
                                                          OUTPUT_FILE="${1}"
                                                          ;;
        -c | --config-file )                              shift
                                                          CONFIG_FILE="${1}"
                                                          ;;
        -h | --help )                                     usage
                                                          exit
                                                          ;;
        * )                                               usage
                                                          exit 1
    esac
    shift
done


DEPLOYMENT_TEMPLATE=${DEPLOYMENT_TEMPLATE:-${DEFAULT_DEPLOYMENT_TEMPLATE}}
CONFIG_FILE=${CONFIG_FILE:-${DEFAULT_CONFIG_FILE}}
OUTPUT_FILE=${OUTPUT_FILE:-${DEFAULT_OUTPUT_FILE}}

echo "Configuring deployment using following:"
echo "DEPLOYMENT_TEMPLATE = ${DEPLOYMENT_TEMPLATE}"
echo "CONFIG_FILE = ${CONFIG_FILE}"
echo "OUTPUT_FILE = ${OUTPUT_FILE}"
python $SCRIPT_PATH/template_deploy.py --resource-name=${RESOURCE_NAME} \
    --namespace=${K8S_NAMESPACE} \
    --deployment-template=${DEPLOYMENT_TEMPLATE} \
    --config-file=${CONFIG_FILE} --output-file=${OUTPUT_FILE}
