#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash
set -e

target=${1:-local}

THIS_DIR="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
GEN_DIR="${THIS_DIR}/generated-container-model"
PYTHON_VERSION=${PYTHON_VERSION:-3.6}  # or 3.7 or 3.8
NAMESPACE=certifai-models

function base_setup() {
  model_type=$1
  image_name=$2
  model_file=$3
  echo "***Generating ${model_type}***"
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
  if [ $target == "local" ]; then
    end_prediction_service_local
  elif [ $target == "minikube" ]; then
    end_prediction_service_minikube
  fi
  result=failed # set for next test, until it explicitly succeeds
}


function end_prediction_service_local() {
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
}

function end_prediction_service_minikube() {
  if [ ${result} = 'failed' ]
  then
    kubectl logs -l app=${resource_name} --namespace $NAMESPACE
  fi
  kubectl delete service ${resource_name} --ignore-not-found --namespace $NAMESPACE
  kubectl delete deployment ${resource_name} --ignore-not-found --namespace $NAMESPACE
}

trap end_prediction_service EXIT

function build() {
  image_name=$1
  echo "***Building ${image_name}***"
  sh ${GEN_DIR}/container_util.sh build
}

function minikube_setup() {
  eval $(minikube docker-env) # build images in shared registry
  # setup minio server on local port 9000
  kubectl apply -f examples/minikube/test-minio.yml
  kubectl get svc test-minio 2>&1 > /dev/null
  if [ "$?" -ne 0 ]; then
    kubectl expose deployment test-minio --type=LoadBalancer --port 9000 --target-port 9000
  fi
  echo "***Setting up minio command line (mc) and certifai bucket***"
  mc config host list minikube 2>&1 > /dev/null
  if [ "$?" -ne 0 ]; then
    mc config host add minikube http://127.0.0.1:9000 minio minio123
  fi
  mc ls minikube/certifai 2>&1 > /dev/null
  if [ "$?" -ne 0 ]; then
    mc mb minikube/certifai
  fi
  mc cp ${THIS_DIR}/license.txt minikube/certifai/files/license.txt
}

function data_setup() {
  local_name=$1
  model_file=$2
  model_use_case_id=$3
  if [ $target == "local" ]; then
    return 0
  fi
  echo "***Setting up prediction service data in minio for ${local_name}***"
  mc config host add minikube http://127.0.0.1:9000 minio minio123
  model_data_path="minikube/certifai/${model_use_case_id}/models"
  local_path="${THIS_DIR}/${local_name}/model"
  mc cp ${local_path}/${model_file} ${model_data_path}/${model_file}
  mc cp ${local_path}/metadata.yml ${model_data_path}/metadata.yml
}

function run_and_test() {
  local_name=$1
  model_file=$2
  image_name=$3
  resource_name=$4
  if [ $target == "local" ]; then
    echo "***Running ${local_name}***"
    container_id=$(docker run -d -p 8551:8551 -v ${THIS_DIR}/${local_name}/model:/tmp/model \
      -e MODEL_PATH=/tmp/model/${model_file} \
      -e METADATA_PATH=/tmp/model/metadata.yml  -t ${image_name})
  elif [ $target == "minikube" ]; then
    echo "***Generating deployment definition for ${resource_name}***"
    sh ${GEN_DIR}/config_deploy.sh -c ${THIS_DIR}/${local_name}/model/deployment_config.yml
    kubectl apply -f ${GEN_DIR}/deployment.yml
    kubectl wait --for=condition=ready --timeout=300s pod -l app=${resource_name} -n ${NAMESPACE}
    # we need to delete the created service so expose can create it
    kubectl delete svc ${resource_name} --ignore-not-found --namespace certifai-models
    kubectl expose deployment ${resource_name} --type=LoadBalancer \
      --port 8551 --target-port 8551 --namespace certifai-models
  fi
  # Wait until health endpoint is available
  wait_for 'curl -X GET http://127.0.0.1:8551/health'
  echo "***Testing ${local_name}***"
  certifai scan -f ${THIS_DIR}/${local_name}/explain_def.yml
  echo "***Successfully tested ${local_name}***"
  end_prediction_service succeeded
}


# Install the toolkit, if its not already installed
if ! command -v certifai &> /dev/null
then
  pip install ${THIS_DIR}/certifai_toolkit/packages/all/*
  pip install ${THIS_DIR}/certifai_toolkit/packages/python${PYTHON_VERSION}/*
fi

#
# MAIN EXECUTION STARTS HERE
#
set -exv

if [ $target == "local" ]; then
  echo "Running local prediction service tests"
elif [ $target == "minikube" ]; then
  echo "Running minikube prediction service tests"
  minikube_setup
else
  echo "Invalid target environment"
  exit 1
fi


# Predict service for H2O MOJO
h2o_setup h2o_mojo h2o_mojo_predict
build h2o_mojo_predict
for name in auto_insurance german_credit iris
do
  local_name="h2o_${name}"
  muc_id="test_${name}"
  model_id="dai-mojo"
  data_setup ${local_name} pipeline.mojo ${muc_id}
  name_dashed=$(echo ${muc_id}-${model_id} | tr '_' '-')
  run_and_test ${local_name} pipeline.mojo h2o_mojo_predict "${name_dashed}"
done

train_models # For the non-H2O models
#
# Predict service for Sklearn
python_setup python sklearn_predict
build sklearn_predict
data_setup sklearn_german_credit model.pkl test_german_credit
run_and_test sklearn_german_credit model.pkl sklearn_predict test-german-credit-dtree

# Predict service for XGBClassifier or XGBRegressor
python_setup python xgboost_predict
# Add xgboost to requirements
echo "\nxgboost==1.2.0\n" >>  ${GEN_DIR}/requirements.txt
build xgboost_predict
data_setup xgboost_iris model.pkl test_iris
run_and_test xgboost_iris model.pkl xgboost_predict test-iris-xgb-iris
#
#
# Predict service for xgboost using DMatrix
python_setup python_xgboost_dmatrix xgboost_dmatrix_predict
build xgboost_dmatrix_predict
data_setup xgboost_dmatrix_income model.pkl test_income
run_and_test xgboost_dmatrix_income model.pkl xgboost_dmatrix_predict test-income-xgboost

echo "***All tests completed successfully***"
trap - EXIT
