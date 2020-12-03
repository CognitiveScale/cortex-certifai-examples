#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash
set -e

THIS_DIR="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
GEN_DIR="${THIS_DIR}/generated-container-model"
PYTHON_VERSION=${PYTHON_VERSION:-3.6}  # or 3.7 or 3.8


function base_setup() {
  model_type=$1
  image_name=$2
  model_file=$3
  echo "***Generating ${name}***"
  rm -rf ${GEN_DIR}
  sh ${THIS_DIR}/../generate.sh -i ${image_name}:latest -m ${model_type} -d ${GEN_DIR}

  all_dir=${GEN_DIR}/packages/all
  mkdir -p ${all_dir}
  cp ${THIS_DIR}/certifai_toolkit/packages/all/cortex-certifai-common*.zip ${all_dir}
  cp ${THIS_DIR}/certifai_toolkit/packages/all/cortex-certifai-model*.zip ${all_dir}

}

function h2o_setup() {
  base_setup $1 $2 pipeline.mojo
  cp ${THIS_DIR}/license.txt ${GEN_DIR}/license/license.txt
  cp ${THIS_DIR}/daimojo*linux_x86_64.whl ${GEN_DIR}/ext_packages/
}

MODEL_DIR=${THIS_DIR}/../..
function train_models() {
  (cd  ${MODEL_DIR}/german_credit && python train.py)
  cp ${MODEL_DIR}/german_credit/german_credit_dtree.pkl ${THIS_DIR}/sklearn_german_credit/model/model.pkl
  (cd  ${MODEL_DIR}/income_prediction && python train.py)
  cp ${MODEL_DIR}/income_prediction/adult_income_xgb.pkl ${THIS_DIR}/xgboost_dmatrix_income/model/model.pkl
  (cd  ${MODEL_DIR}/iris && python train.py)
  cp ${MODEL_DIR}/iris/iris_xgb.pkl ${THIS_DIR}/xgboost_iris/model/model.pkl
}

function python_setup() {
  base_setup $1 $2 model.pkl
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
  if [ ${result} = 'failed' ]
  then
    echo "!!!TEST FAILED for ${name}!!!"
  fi
  echo "Removing running prediction service, if any"
  if [ -n "$container_id" ]
  then
    if [ ${result} = 'failed' ]
    then
      docker logs ${container_id}
    fi
    docker stop ${container_id}
    docker rm -f ${container_id}
  fi
  unset container_id
  result=failed # unless it explicitly succeeds
}
trap end_prediction_service EXIT

function build() {
  image_name=$1
  echo "***Building ${image_name}***"
  sh ${GEN_DIR}/container_util.sh build
}

function run_and_test() {
  name=$1
  model_file=$2
  image_name=$3
  echo "***Running ${name}***"
  container_id=$(docker run -d -p 8551:8551 -v ${THIS_DIR}/${name}/model:/tmp/model \
    -e MODEL_PATH=/tmp/model/${model_file} \
    -e METADATA_PATH=/tmp/model/metadata.yml  -t ${image_name})
  # Wait until health endpoint is available
  wait_for 'curl -X GET http://127.0.0.1:8551/health'
  echo "***Testing ${name}***"
  certifai scan -f ${THIS_DIR}/${name}/explain_def.yml
  echo "***Successfully tested ${name}***"
  end_prediction_service succeeded
}

# Install the toolkit, if its not already installed
if ! command -v certifai &> /dev/null
then
  pip install ${THIS_DIR}/certifai_toolkit/packages/all/*
  pip install ${THIS_DIR}/certifai_toolkit/packages/python${PYTHON_VERSION}/*
fi

#
set -exv

# Predict service for H2O MOJO
h2o_setup h2o_mojo h2o_mojo_predict
build h2o_mojo_predict
for name in h2o_auto_insurance h2o_german_credit h2o_iris
do
  run_and_test ${name} pipeline.mojo h2o_mojo_predict
done

train_models

# Predict service for Sklearn
python_setup python sklearn_predict
build sklearn_predict
run_and_test sklearn_german_credit model.pkl sklearn_predict

# Predict service for XGBClassifier or XGBRegressor
python_setup python xgboost_predict
# Add xgboost to requirements
echo "\nxgboost==1.2.0\n" >>  ${GEN_DIR}/requirements.txt
build xgboost_predict
run_and_test xgboost_iris model.pkl xgboost_predict

# Predict service for xgboost using DMatrix
python_setup python_xgboost_dmatrix xgboost_dmatrix_predict
build xgboost_dmatrix_predict
run_and_test xgboost_dmatrix_income model.pkl xgboost_dmatrix_predict

echo "***All tests completed successfully***"
trap - EXIT
