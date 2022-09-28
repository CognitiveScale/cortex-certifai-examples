#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function usage() {
  printf "Usage: upload_artifact.sh <endpoint> <access-key> <secret-key> <bucket-name>\n"
  exit 1
}

END_POINT=$1
ACCESS_KEY=$2
SECRET_KEY=$3
BUCKET_NAME=$4

if [[ -z $BUCKET_NAME  ]]; then
    echo "ERROR: Missing bucket"
    usage
fi

echo "uploading deployment files .."

mc alias set profile $END_POINT $ACCESS_KEY $SECRET_KEY

mc cp --recursive $DIR/deployment profile/$BUCKET_NAME/data

mc cp --recursive $DIR/files profile/$BUCKET_NAME/data
