#
# Copyright (c) 2023. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash
set -e

# - ask in Trusted AI chat if we still have an h2o license?

function set_globals() {
  THIS_DIR="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
  GEN_DIR="${THIS_DIR}/generated-container-model"
  PYTHON_VERSION=${PYTHON_VERSION:-3.8}  # or 3.7
  XGBOOST_VERSION="xgboost==1.7.2"
  NAMESPACE=certifai-models
  MODEL_DIR=${THIS_DIR}/../..
  RUN_H2O=${RUN_H2O-"false"}
  MINIO="mc"

  # Default toolkit to './certifai_toolkit'
  TOOLKIT_PATH="${TOOLKIT_PATH:-$THIS_DIR/certifai_toolkit}"
  PACKAGES_DIR="${TOOLKIT_PATH}/packages"
}

function check_minio_installed() {
  if ! command -v $MINIO &> /dev/null
  then
      echo "'$MINIO' CLI could not be found! Install Minio Client: https://min.io/docs/minio/linux/reference/minio-mc.html"
      exit 1
  fi
}

function base_setup() {
  model_type=$1
  image_name=$2
  model_file=$3
  echo "***Generating ${model_type}***"
  rm -rf "${GEN_DIR}"
  "${THIS_DIR}/../generate.sh" -i "${image_name}":latest -m "${model_type}" -d "${GEN_DIR}" -t "$TOOLKIT_PATH"

  all_dir=${GEN_DIR}/packages/all
  mkdir -p "${all_dir}"
  cp "${PACKAGES_DIR}"/all/cortex-certifai-common*.zip "${all_dir}"
  cp "${PACKAGES_DIR}"/all/cortex-certifai-model*.zip "${all_dir}"

}

function h2o_setup() {
  base_setup "$1" "$2" pipeline.mojo
  cp "${THIS_DIR}"/license.txt "${GEN_DIR}"/license/license.txt
  cp "${THIS_DIR}"/daimojo*linux_x86_64.whl "${GEN_DIR}"/ext_packages/
}

function train_models() {
  (cd  "${MODEL_DIR}"/german_credit && python train.py)
  cp "${MODEL_DIR}"/german_credit/models/german_credit_dtree.pkl "${THIS_DIR}"/sklearn_german_credit/model/model.pkl
  (cd  "${MODEL_DIR}"/income_prediction && python train.py)
  cp "${MODEL_DIR}"/income_prediction/adult_income_xgb.pkl "${THIS_DIR}"/xgboost_dmatrix_income/model/model.pkl
  (cd  "${MODEL_DIR}"/iris && python train.py)
  cp "${MODEL_DIR}"/iris/iris_xgb.pkl "${THIS_DIR}"/xgboost_iris/model/model.pkl
}

function python_setup() {
  base_setup "$1" "$2" model.pkl
}

function wait_for() {
  command="$1"
  next_wait_time=0
  until [ $next_wait_time -eq 30 ] || $(command); do
      sleep $(( next_wait_time=next_wait_time+5 ))
  done
  [ "$next_wait_time" -lt 30 ]
}

function end_prediction_service() {
  result=${1:-failed}
  if [ "${result}" = 'failed' ]
  then
    echo "!!!TEST FAILED for ${name}!!!"
  fi
  echo "Removing running prediction service, if any"
  if [ "$target" == "local" ]; then
    end_prediction_service_local
  elif [ "$target" == "minikube" ]; then
    end_prediction_service_minikube
  fi
  result=failed # set for next test, until it explicitly succeeds
}


function end_prediction_service_local() {
  if [ -n "$container_id" ]
  then
    if [ "${result}" = 'failed' ]
    then
      docker logs "${container_id}"
    fi
    docker stop "${container_id}"
    docker rm -f "${container_id}"
  fi
  unset container_id
}

function end_prediction_service_minikube() {
  if [ "${result}" = 'failed' ]
  then
    kubectl logs -l app="${resource_name}" --namespace $NAMESPACE
  fi
  kubectl delete service "${resource_name}" --ignore-not-found --namespace $NAMESPACE
  kubectl delete deployment "${resource_name}" --ignore-not-found --namespace $NAMESPACE
}

function build() {
  image_name=$1
  echo "***Building ${image_name}***"
  sh "${GEN_DIR}"/container_util.sh build
}

function minikube_setup() {
  eval $(minikube docker-env) # build images in shared registry
  # setup minio server on local port 9000
  set +e
  kubectl create namespace "$NAMESPACE"
  kubectl apply -f "${THIS_DIR}"/minikube/test-minio.yml
  sleep 5  #  wait for service to come up
  #kubectl get svc test-minio 2>&1 > /dev/null
  #if [ "$?" -ne 0 ]; then
  if kubectl get svc test-minio >> /dev/null; then
    kubectl expose deployment test-minio --type=LoadBalancer --port 9000 --target-port 9000
  fi
  echo "***Setting up minio command line ($MINIO) and certifai bucket***"
  $MINIO config host list minikube 2>&1 > /dev/null
  if [ "$?" -ne 0 ]; then
    $MINIO config host add minikube http://127.0.0.1:9000 minio minio123
  fi
  $MINIO ls minikube/certifai 2>&1 > /dev/null
  if [ "$?" -ne 0 ]; then
    $MINIO mb minikube/certifai
  fi

  if [[ "$RUN_H2O" == "true" ]]; then
    $MINIO cp "${THIS_DIR}"/license.txt minikube/certifai/files/license.txt
  fi
  set -e
}

function data_setup() {
  local_name=$1
  model_file=$2
  model_use_case_id=$3
  if [ "$target" == "local" ]; then
    return 0
  fi
  echo "***Setting up prediction service data in minio for ${local_name}***"
  $MINIO config host add minikube http://127.0.0.1:9000 minio minio123
  model_data_path="minikube/certifai/${model_use_case_id}/models"
  local_path="${THIS_DIR}/${local_name}/model"
  $MINIO cp "${local_path}"/"${model_file}" "${model_data_path}"/"${model_file}"
  $MINIO cp "${local_path}"/metadata.yml "${model_data_path}"/metadata.yml
}

function run_and_test() {
  local_name=$1
  model_file=$2
  image_name=$3
  resource_name=$4
  if [ "$target" == "local" ]; then
    echo "***Running ${local_name}***"
    container_id=$(docker run -d -p 8551:8551 -v "${THIS_DIR}"/"${local_name}"/model:/tmp/model \
      -e MODEL_PATH=/tmp/model/"${model_file}" \
      -e METADATA_PATH=/tmp/model/metadata.yml  -t "${image_name}")
  elif [ "$target" == "minikube" ]; then
    echo "***Generating deployment definition for ${resource_name}***"
    sh "${GEN_DIR}"/config_deploy.sh -c "${THIS_DIR}"/"${local_name}"/model/deployment_config.yml
    kubectl apply -f "${GEN_DIR}"/deployment.yml
    kubectl wait --for=condition=ready --timeout=300s pod -l app="${resource_name}" -n ${NAMESPACE}
    # we need to delete the created service so expose can create it
    kubectl delete svc "${resource_name}" --ignore-not-found --namespace certifai-models
    kubectl expose deployment "${resource_name}" --type=LoadBalancer \
      --port 8551 --target-port 8551 --namespace certifai-models
  fi
  # Wait until health endpoint is available
  wait_for 'curl -X GET http://127.0.0.1:8551/health'
  echo "***Testing ${local_name}***"
  certifai scan -f "${THIS_DIR}"/"${local_name}"/explain_def.yml
  echo "***Successfully tested ${local_name}***"
  end_prediction_service succeeded
}

function install_toolkit() {
  # Install the toolkit, if its not already installed
  if ! command -v certifai &> /dev/null
  then
    echo "Installing Certifai Toolkit!"
    pip install "${THIS_DIR}"/certifai_toolkit/packages/all/*
    pip install "${THIS_DIR}"/certifai_toolkit/packages/python"${PYTHON_VERSION}"/*
  fi
}


function run_sklearn_model() {
  # Predict service for Sklearn
  python_setup python sklearn_predict
  build sklearn_predict
  data_setup sklearn_german_credit model.pkl test_german_credit
  run_and_test sklearn_german_credit model.pkl sklearn_predict test-german-credit-dtree
}

function run_xgboost_iris_model() {
   # Predict service for XGBClassifier or XGBRegressor
  python_setup python xgboost_predict
  # Add xgboost to requirements
  echo "\n$XGBOOST_VERSION\n" >>  "${GEN_DIR}"/requirements.txt
  build xgboost_predict
  data_setup xgboost_iris model.pkl test_iris
  run_and_test xgboost_iris model.pkl xgboost_predict test-iris-xgb-iris
}

function run_xgboost_income_prediction() {
  # Predict service for xgboost using DMatrix
  python_setup python_xgboost_dmatrix xgboost_dmatrix_predict
  build xgboost_dmatrix_predict
  data_setup xgboost_dmatrix_income model.pkl test_income
  run_and_test xgboost_dmatrix_income model.pkl xgboost_dmatrix_predict test-income-xgboost
}

function run_h2o_models() {
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
    run_and_test "${local_name}" pipeline.mojo h2o_mojo_predict "${name_dashed}"
  done
}


function printUsage() {
  local prog_name
  prog_name="$(basename "$0")"

  local usage
  usage="$prog_name [-h|--help] [local | minikube]

Test Containerized Model examples using the Certifai Model SDK.

Options:

  local - Run local prediction service tests

  minikube - Run minikube prediction service tests. Requires Minikube to already be running.

Environment Variables:

  RUN_H2O - if 'true', then h2o examples will be tested and the 'license.txt' must contain a valid h2o license.
            Defaults to 'false'.

  TOOLKIT_PATH - The path to the (unzipped) Certifai Toolkit, defaults to: ./certifai_toolkit

Examples:

  TOOLKIT_PATH=./toolkit ./run_test.sh local

  TOOLKIT_PATH=./toolkit ./run_test.sh minikube
"
   echo "$usage"
}

#
# MAIN EXECUTION STARTS HERE
#

function main() {
  target=${1:-local}
  set -exv
  set_globals
  install_toolkit
  if [ "$target" == "local" ]; then
    echo "Running local prediction service tests"
  elif [ "$target" == "minikube" ]; then
    echo "Running minikube prediction service tests"
    check_minio_installed
    minikube_setup
  elif [ "$target" == "-h" ] || [ "$target" == "--help" ]; then
    printUsage
    exit 0
  else
    echo "Invalid target environment"
    printUsage
    exit 1
  fi

  # catch any EXIT signals & clean prediction services
  trap end_prediction_service EXIT
  if [[ "$RUN_H2O" == "true" ]]; then
    run_h2o_models
  fi
  # Train the non-H2O models
  train_models
  # Run the non-H2O models
  run_sklearn_model
  run_xgboost_iris_model
  run_xgboost_income_prediction
  echo "***All tests completed successfully***"
  trap - EXIT
}

main "$@"
