#!/bin/bash
set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function usage() {
  printf "Usage: upload_artifact_azure.sh <container-name> <destination-path> <account-name> <sas-token>\n"
  exit 1
}

CONTAINER_NAME=$1
DIRECTORY_NAME=$2
ACCOUNT_NAME=$3
SAS_TOKEN=$4

if [[ -z $CONTAINER_NAME  ]]; then
    echo "ERROR: Missing destination container name"
    usage
fi

if [[ -z $DIRECTORY_NAME  ]]; then
    echo "ERROR: Missing destination directory name"
    usage
fi

if [[ -z $ACCOUNT_NAME  ]]; then
    echo "ERROR: Missing storage account name"
    usage
fi

if [[ -z $DIRECTORY_NAME  ]]; then
    echo "ERROR: Missing SAS TOKEN"
    usage
fi

echo "Uploading deployment files .."

az storage fs directory upload --recursive \
  --file-system "${CONTAINER_NAME}" \
  --source "${DIR}/deployment" \
  --destination-path "${DIRECTORY_NAME}" \
  --account-name "${ACCOUNT_NAME}" \
  --sas-token "${SAS_TOKEN}"

az storage fs directory upload --recursive \
  --file-system "${CONTAINER_NAME}" \
  --source "${DIR}/files" \
  --destination-path "${DIRECTORY_NAME}" \
  --account-name "${ACCOUNT_NAME}" \
  --sas-token "${SAS_TOKEN}"
