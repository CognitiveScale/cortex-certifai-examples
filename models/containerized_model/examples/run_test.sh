#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash
set -e

THIS_DIR="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
GEN_DIR="${THIS_DIR}/generated-container-model"
PYTHON_VERSION=${PYTHON_VERSION:-3.6}  # or 3.7 or 3.8

function h2o_setup() {
  name=$1
  rm -rf ${GEN_DIR}
  sh ${THIS_DIR}/../generate.sh -i ${name}:latest -m "h2o_mojo"

  for f in model/metadata.yml model/pipeline.mojo
  do
    cp ${THIS_DIR}/${name}/${f} ${GEN_DIR}/${f}
  done

  cp ${THIS_DIR}/license.txt ${GEN_DIR}/license/license.txt
  cp ${THIS_DIR}/daimojo*linux_x86_64.whl ${GEN_DIR}/ext_packages/
  all_dir=${GEN_DIR}/packages/all
  mkdir -p ${all_dir}
  cp ${THIS_DIR}/certifai_toolkit/packages/all/cortex-certifai-common*.zip ${all_dir}
  cp ${THIS_DIR}/certifai_toolkit/packages/all/cortex-certifai-model*.zip ${all_dir}
}

function wait_for() {
  command="$1"
  next_wait_time=0
  until [ $next_wait_time -eq 30 ] || $(command); do
      sleep $(( next_wait_time=next_wait_time+5 ))
  done
  [ $next_wait_time -lt 30 ]
}

function end_prediction_service() {
  result=${1:-failed}
  echo "Removing running prediction service, if any"
  if [ -n "$container_id" ]
  then
    if [ ${result} = 'failed' ]
    then
      docker logs ${container_id}
    fi
    docker stop ${container_id}
    docker rm -f ${container_id}
    if [ ${result} = 'failed' ]
    then
      echo "!!!TEST FAILED for ${name}!!!"
    fi
  fi
  unset container_id
}

trap end_prediction_service EXIT

# Install the toolkit, if its not already installed
if ! command -v certifai &> /dev/null
then
  pip install ${THIS_DIR}/certifai_toolkit/packages/all/*
  pip install ${THIS_DIR}/certifai_toolkit/packages/python${PYTHON_VERSION}/*
fi

#
set -exv
for name in h2o_auto_insurance h2o_german_credit h2o_iris
do
  echo "***Building ${name}***"
  h2o_setup $name
  sh ${GEN_DIR}/container_util.sh build
  echo "***Running ${name}***"
  container_id=$(docker run -d -p 8551:8551 --env-file ${GEN_DIR}/environment.yml  -t ${name})
  # Wait until health endpoint is available
  wait_for 'curl -X GET http://127.0.0.1:8551/health'
  echo "***Testing ${name}***"
  certifai explain -f ${THIS_DIR}/${name}/explain_def.yml
  echo "***Successfully tested ${name}***"
  end_prediction_service succeeded

done
