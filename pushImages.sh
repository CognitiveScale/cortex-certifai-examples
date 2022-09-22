#!/bin/bash -eux
#
##

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
ARTIFACTS_DIR="${SCRIPT_PATH}/artifacts"
BUILD_REPORT="${ARTIFACTS_DIR}/buildReport.txt"

while read p; do
  docker push "$p"
done < ${BUILD_REPORT}

which jq