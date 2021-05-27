#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

AWS_BUCKET=$1

if [[ -z $AWS_BUCKET  ]]; then
    echo "ERROR: Missing s3://AWS_BUCKET "
    exit 1
fi

echo "make sure aws credentials are setup for upload to work"
echo "uploading deployment files .."

aws s3 cp --recursive $DIR/deployment $AWS_BUCKET/data/deployment

aws s3 cp --recursive $DIR/files $AWS_BUCKET/data/files

