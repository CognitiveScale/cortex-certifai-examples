#!/usr/bin/env bash
#
##
set -xeuf -o pipefail

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
DEPLOYMENT_DIR="${SCRIPT_PATH}/scan-manager/docs/setup_artifacts/deployment"
CONFIG_FILENAME="config.yml"
OUT_DIR="/tmp/docker_scans"

function scanBaseImageLocally() {
  # $1 = base_image
  # $2 = output filename
  docker scan "$1" >> "$2" || true  # ignore fails due to vulnerabilities
}

function _trim() {
  # Removes whitespace & newlines
  # $1 = string to trim
  echo "${1}" | sed 's/ //g' | sed 's/\\n//g'
  #echo "${1}" | tr d ' ' | tr -d '\\n'
}

function main() {
  mkdir -p  ${OUT_DIR}
  readarray base_images < <(yq 'to_entries | map(.value.available_base_images) | flatten | map(.value) | unique | .[]' "${DEPLOYMENT_DIR}"/"${CONFIG_FILENAME}")
  local length=${#base_images[@]}
  for ((i = 0; i < length; ++i)); do
    local base_image
    base_image=$(_trim "${base_images[$i]}")
    local out_file="${OUT_DIR}/scan_${i}"

    echo "Scanning Base image: ${base_image}, writing to output: ${out_file}"
    scanBaseImageLocally "${base_image}" "${out_file}"
  done
}
main
