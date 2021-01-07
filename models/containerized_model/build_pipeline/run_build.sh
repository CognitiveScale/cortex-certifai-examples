#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash
set -e

image_name=${1:-my-model}
model_type=${2:-h2o_mojo}

THIS_DIR="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
GEN_DIR="${THIS_DIR}/generated-container-model"
PYTHON_VERSION=${PYTHON_VERSION:-3.6}  # or 3.7 or 3.8

function base_setup() {
  model_type=$1
  image_name=$2
  echo "***Generating ${model_type}***"
  rm -rf ${GEN_DIR}
  sh ${THIS_DIR}/../generate.sh -i ${image_name}:latest -m ${model_type} -d ${GEN_DIR}

  all_dir=${GEN_DIR}/packages/all
  mkdir -p ${all_dir}
  cp ${THIS_DIR}/certifai_toolkit/packages/all/cortex-certifai-common*.zip ${all_dir}
  cp ${THIS_DIR}/certifai_toolkit/packages/all/cortex-certifai-model*.zip ${all_dir}

  cp -R ${image_name}/src/* ${GEN_DIR}/src
}

function h2o_setup() {
  base_setup $1 $2
  cp ${THIS_DIR}/daimojo*linux_x86_64.whl ${GEN_DIR}/ext_packages/
}

MODEL_DIR=${THIS_DIR}/../..


function build() {
  image_name=$1
  echo "***Building ${image_name}***"
  sh ${GEN_DIR}/container_util.sh build
}

# Install the toolkit, if its not already installed
if ! command -v certifai &> /dev/null
then
  pip install ${THIS_DIR}/certifai_toolkit/packages/all/*
  pip install ${THIS_DIR}/certifai_toolkit/packages/python${PYTHON_VERSION}/*
fi

set -exv

if [ "$model_type" = 'h2o_mojo' ]
then
  h2o_setup $model_type $image_name
else
  base_setup $model_type $image_name
fi
build $image_name

echo "***Build completed successfully***"
