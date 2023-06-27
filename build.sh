#!/bin/bash -eu
#
##
set -eu

function setGlobals() {
  set -x
  PUSH_IMAGES=false
  BUILD_ARM="${BUILD_ARM:-false}"
  SKIP_CONDA="${SKIP_CONDA:-false}"
  SKIP_TOOLKIT="${SKIP_TOOLKIT:-false}"
  RUN_REMOTE_EXAMPLES="${RUN_REMOTE_EXAMPLES:-false}"
  PYTHON_VERSION="3.8"
  SK_PANDAS_VERSION="sklearn-pandas==2.2.0"
  XGBOOST_VERSION="xgboost==1.7.2"
  SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
  ARTIFACTS_DIR="${SCRIPT_PATH}/artifacts"
  TOOLKIT_PATH="${ARTIFACTS_DIR}/certifai_toolkit.zip"
  TOOLKIT_WORK_DIR="${ARTIFACTS_DIR}/toolkit"
  PACKAGES_DIR="${TOOLKIT_WORK_DIR}/packages"
  CONTAINERIZED_EXAMPLES_DIR="${SCRIPT_PATH}/models/containerized_model/examples"
  TEMPLATES_DIR="${SCRIPT_PATH}/models/containerized_model"
  BASE_IMAGES_DIR="${SCRIPT_PATH}/models/containerized_model/base_images"
  NOTEBOOK_DIR="${SCRIPT_PATH}/notebooks"
  TUTORIALS_DIR="${SCRIPT_PATH}/tutorials"
  BUILD_REPORT_JSON="${ARTIFACTS_DIR}/buildReport.json"
  BASE_IMAGE_BUILD_REPORT_JSON="${ARTIFACTS_DIR}/baseImageBuildReport.json"
  ENV_FILE="${ARTIFACTS_DIR}/.env"
  AWS_ENV_FILE="${ARTIFACTS_DIR}/.aws_env"
  AZURE_ENV_FILE="${ARTIFACTS_DIR}/.azure_env"

  if [ -f "$ENV_FILE" ]; then
    # shellcheck source=/dev/null.
    source "${ENV_FILE}"
  fi
}

function printHelp() {
  # The help message is defined outside of `setGlobals` to avoid echo-ing its value when running the script with -x flag
  local prog_name
  prog_name="$(basename "$0")"

  local usage
  usage="$prog_name [option]

Build and test Certifai examples.

Options:
  CI
      Run all notebook, tutorial, and model examples

  docker
      Build and push Docker images for example containerized model templates

  local-docker
      Build Docker images for example containerized model templates

  docker-builder
      Build and push base Docker images for Prediction Services

  local-docker-builder
    Build base Docker images for Prediction Services

  links
      Test for broken links through Markdown and Jupyter Notebook examples. Recommended to save output to a file, e.g.
        './build.sh links | tee broken-links.txt'

  notebooks
      Run all notebook examples

  tutorials
      Run all tutorial examples

  help
      Print this message

Environment Variables:
  SKIP_CONDA - if 'true', then use the currently activate conda environment (skip creating a new environment)

  SKIP_TOOLKIT - if 'true', then skip installing the Certifai toolkit in the activate conda environment

  RUN_REMOTE_EXAMPLES - if 'true', then examples involving SageMaker or AzureML resources will be run.
    This is 'false' by default to optimize third party resource costs.

  BUILD_ARM - if 'true', then Prediction Service Base Docker Images will be built with the 'linux/arm64' platform.
    False by default (images are built with 'linux/amd64' platform).
"
  echo "${usage}"
}

function activateConda(){
  if [ "${SKIP_CONDA}" = false ]; then
    echo "Creating Certifai conda environment"
    set +u
    eval "$(conda shell.bash hook)"
    conda create -n certifai python="${PYTHON_VERSION}" -y
    conda activate certifai
    conda env list
    which python
    which pip
  else
    echo "Skipping creation of new conda environments, using current Python path.."
  fi
}

function installToolkit() {
  if [ "${SKIP_TOOLKIT}" = false ]; then
    echo "Installing Certifai Toolkit (${TOOLKIT_PATH})"
    extractToolkit
    local cwd="${PWD}"
    cd "${TOOLKIT_WORK_DIR}"

    conda install --file requirements.txt -y
    pip install "${PACKAGES_DIR}"/all/*
    pip install "$(find "${PACKAGES_DIR}/all" -name "cortex-certifai-common-*.zip")[s3,gcp,azure]"
    pip install "$(find "${PACKAGES_DIR}/python${PYTHON_VERSION}" -name "cortex-certifai-engine-*.zip")[shap]"
    cd "${cwd}"
  else
    echo "Skipping installation of Certifai toolkit.."
  fi
}

function getToolkitVersion() {
  extractToolkit
  grep 'Scanner' < "${TOOLKIT_WORK_DIR}/version.txt"  | grep Scanner | cut -d ':' -f 2 | tr -d ' '
}

function extractToolkit() {
  if [ ! -f "${TOOLKIT_PATH}" ]; then
    echo "Certifai toolkit (ZIP) not found found! Toolkit is expected to be at ${TOOLKIT_PATH}"
    exit 1
  fi
  rm -rf "${TOOLKIT_WORK_DIR}"
  unzip -qq -d "${TOOLKIT_WORK_DIR}" "${TOOLKIT_PATH}"
}

function copyPackagesForModels() {
  if [ ! -f "${TOOLKIT_PATH}" ]; then
    echo "Certifai toolkit (ZIP) not found found! Toolkit is expected to be at ${TOOLKIT_PATH}"
    exit 1
  fi
  # Copy ONLY the Common package & Model SDK packages into a relative directory (specifically for models).
  rm -rf "${TEMPLATES_DIR}/packages/all"
  mkdir -p "${TEMPLATES_DIR}/packages/all"
  cp "${PACKAGES_DIR}/all/cortex-certifai-common"* "${TEMPLATES_DIR}/packages/all"
  cp "${PACKAGES_DIR}/all/cortex-certifai-model-sdk"*  "${TEMPLATES_DIR}/packages/all"
}

function getExamplesGitSha() {
  git describe --long --always
}

function buildLocal() {
  PUSH_IMAGES=false
  test
  buildModelDeploymentImages
}

function _installModelRequirements() {
  pip install -r "${TEMPLATES_DIR}/requirements.txt"
}

function _installLocalModelRequirements() {
  pip install "$SK_PANDAS_VERSION" "$XGBOOST_VERSION"
}


function buildModelDeploymentImages() {
  # Builds Docker images for the example Containerized Model Types (Scikit, H2O, Proxy, R). These are images are used
  # for the default Model Types in Scan Manager in Certifai Enterprise Version 1.3.16 and earlier.
  #
  # We have to enforce a versioning strategy in the example model templates. Part of the trouble here is that template
  # images install the Certifai packages, so we should tag them in such a way to show that version.
  #
  # Current tagging strategy: `<version-counter>-<certifai-toolkit-version>`
  #
  #   `<version-counter>` is a running count we maintain based on the base image, Python version, & other dependencies
  #
  # Examples:
  #   c12e/cortex-certifai-model-scikit:v3-1.3.11-120-g5d13c272
  #   c12e/cortex-certifai-model-h2o-mojo:v4-1.3.17-19-g66a6ae33
  #   c12e/cortex-certifai-hosted-model:v4-1.3.17-19-g66a6ae33
  #   c12e/cortex-certifai-model-r:v4-1.3.17-19-g66a6ae33
  #
  # The main reason for this tagging strategy is that earlier images were tagged with 'v1', v2, etc.
  local certifai_version
  certifai_version=$(getToolkitVersion)

  local version
  version="v4-${certifai_version}"
  echo "##### BUILDING ${version} ######"

  local scikit_image="c12e/cortex-certifai-model-scikit:${version}"
  local h2o_image="c12e/cortex-certifai-model-h2o-mojo:${version}"
  local proxy_image="c12e/cortex-certifai-hosted-model:${version}"
  local r_image="c12e/cortex-certifai-model-r:${version}"

  _buildTemplate "${scikit_image}" python
  _buildTemplate "${h2o_image}" h2o_mojo
  _buildTemplate "${proxy_image}" proxy

   # TODO: The base image rocker/r-apt:bionic` is outdated, but the image fails to build when using
   # `rocker/r-ver:3.6.1` or `rocker/r-ver:latest` because `r-cran-aws.s3` is not found.
  _buildTemplate "${r_image}" r_model rocker/r-apt:bionic

  echo "{\"scikit\": \"${scikit_image}\", \"h2o\": \"${h2o_image}\", \"proxy\": \"${proxy_image}\", \"r\": \"${r_image}\" }" > "${BUILD_REPORT_JSON}"
}

function _buildTemplate() {
  # Generates a Containerized Model template and builds a docker image with the contents. Arguments are for the
  # ./generate.sh script.
  # $1 image
  # $2 model-type
  # $3 base-image (optional)
  local out_dir=/tmp/work
  rm -rf "${out_dir}"
  cd "${TEMPLATES_DIR}"

  local base_image="${3:-}"
  if [ -z "$base_image" ]; then
    ./generate.sh --target-docker-image "$1" \
                --dir "${out_dir}" \
                --model-type "$2" \
                --toolkit-path "$TOOLKIT_WORK_DIR"
                # explicitly use default base image
  else
    ./generate.sh --target-docker-image "$1" \
                --dir "${out_dir}" \
                --model-type "$2" \
                --base-docker-image "${base_image}" \
                --toolkit-path "$TOOLKIT_WORK_DIR"
  fi

  cd "${out_dir}"
  ./container_util.sh build

  if [ "${PUSH_IMAGES}" = true ]; then
    echo "Pushing images.."
    docker push "$1"
  else
    echo "Skipping push.."
  fi
}

function buildPredictionServiceBaseImages() {
  # Builds Docker images that act as a base image for generating Containerized Model templates. These are used as base
  # images for Prediction Service in Scan Manager in Certifai Enterprise Version 1.3.17+.
  #
  # We have to enforce a tagging strategy for these images, which will include the Certifai Common & Certifai Model SDK
  # packages along with the `containerized_models/` source code.
  #
  # Current tagging strategy is: `<language>-<certifai-version>-<GIT_SHA>`
  #
  #   `<GIT_SHA>` refers to the commit in this repository that the image was built from
  #
  # Examples:
  #     c12e/cortex-certifai-model-scikit:base-py38-1.3.17-19-g66a6ae33-d389e12
  #     c12e/cortex-certifai-model-scikit:base-py39-1.3.17-19-g66a6ae33-d389e12
  # TODO: Support non-python model types (https://github.com/CognitiveScale/certifai/issues/4775)
  local version
  version="$(getToolkitVersion)-$(getExamplesGitSha)"

  local pythonImageRepo
  pythonImageRepo="c12e/cortex-certifai-model-scikit"

  copyPackagesForModels
  # Resolve docker build architecture and miniconda url for images
  if [[ "${BUILD_ARM}" == "true" ]]; then
    TARGET_PLATFORM="linux/arm64"
    MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
  else
    TARGET_PLATFORM="linux/amd64"
    MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  fi

  local py38_image="${pythonImageRepo}:base-py38-${version}"
  docker build --platform=$TARGET_PLATFORM --pull --rm -f "${BASE_IMAGES_DIR}/Dockerfile.cortex-certifai-python-model-base" \
      --build-arg TOOLKIT_PATH=. \
      --build-arg PY_VERSION=3.8 \
      --build-arg MINICONDA_URL=$MINICONDA_URL \
      -t "$py38_image" "${TEMPLATES_DIR}"

  local py39_image="${pythonImageRepo}:base-py39-${version}"
  docker build --platform=$TARGET_PLATFORM --pull --rm -f "${BASE_IMAGES_DIR}/Dockerfile.cortex-certifai-python-model-base" \
      --build-arg TOOLKIT_PATH=. \
      --build-arg PY_VERSION=3.9 \
      --build-arg MINICONDA_URL=$MINICONDA_URL \
      -t "$py39_image" "${TEMPLATES_DIR}"

  if [ "${PUSH_IMAGES}" = true ]; then
    echo "Pushing images.."
    docker push "$py38_image"
    docker push "$py39_image"
  else
    echo "Skipping push.."
  fi

  # Write build Report
  echo "{\"python38\": \"${py38_image}\", \"python39\": \"${py39_image}\"}" > "${BASE_IMAGE_BUILD_REPORT_JSON}"
}

function testAll() {
  testMarkdownLinks
  testModels
  testNotebooks
  testTutorials
  # Requires Docker/Minikube - so skipped in pipeline
  #testContainerizedModels
}

function testMarkdownLinks() {
  # Convert all notebooks to markdown to perform broken link detection on notebooks as well as README files
  # shellcheck disable=SC2038
  find . -name "*.ipynb" -not -path ".ipynb_checkpoints" -not -path "*/.ipynb_checkpoints/*" -exec echo \'{}\' \; | \
    xargs jupyter nbconvert --to markdown

  # Python alternative -> https://github.com/linkchecker/linkchecker - supports markdown but intended for HTML or urls
  # However this requires a .linkcheckerrc file (with markdown plugin) -> linkchecker -f .linkcheckerrc --check-extern .
  if ! type "markdown-link-check" > /dev/null;
  then
    echo "********************"
    echo "markdown-link-check is not installed, it will be installed globally with npm"
    echo "https://github.com/tcort/markdown-link-check"
    npm install -g markdown-link-check@3.10.3
    echo "********************"
  else
    echo "markdown-link-check already installed"
  fi
  # shellcheck disable=SC2038
  if find . -name "*.md" -not -path ".ipynb_checkpoints" -not -path "*/.ipynb_checkpoints/*" -exec echo \'{}\' \; | xargs markdown-link-check -c config.json;
  then
    echo "No broken links found!"
  else
    echo "Broken links found! Exiting..." >&2
    exit 1
  fi
}

function testModels() {
  MODELS_DIR="${SCRIPT_PATH}/models"
  # run tests for each individual example
  cd "$MODELS_DIR"/german_credit/
  python -m unittest -v test.py

  cd "$MODELS_DIR"/german_credit_pandas
  python -m unittest -v test.py

  cd "$MODELS_DIR"/income_prediction
  python -m unittest -v test.py

  cd "$MODELS_DIR"/iris
  python -m unittest -v test.py

  cd "$MODELS_DIR"/patient_readmission
  python -m unittest -v test.py

  # Go back to root directory
  cd  "$SCRIPT_PATH"

  # TODO: Run other examples (see https://github.com/CognitiveScale/certifai/issues/4870)
  # - h2o_dai_german_credit
  # - h2o_dai_regression_auto_insurance
  # - r-models
}

function testContainerizedModels() {
  # run base of set of containerized model examples locally (with docker)
  cd "$CONTAINERIZED_EXAMPLES_DIR"
  TOOLKIT_PATH="$TOOLKIT_WORK_DIR" ./run_test.sh "local"

  # TODO: Add 'RUN_H2O=true' to test other examples (see https://github.com/CognitiveScale/certifai/issues/4870)
  # - h2o_dai_german_credit
  # - h2o_dai_regression_auto_insurance
  # - r-models

  # Go back to root directory
  cd  "$SCRIPT_PATH"
}

function testTutorials() {
  cd "${TUTORIALS_DIR}"
  _installAutomatedDeps
  # bringing_in_your_own_model
  _runNotebookInPlace "${TUTORIALS_DIR}/bringing_in_your_own_model/part_one/BringingInYourOwnModel.ipynb"

  # TODO(LA): This example requires extra set up in the GoCD agent (to communicate with the Certifai dev cluster), might
  # need some help. However, this example exposes some undocumented/fragile APIs (i.e "easy to shoot-yourself in the
  # foot"), so I would vote to not update this and, if possible, maybe even remove it.
  # remote_scan_tutorial
  #_runNotebookInPlace "${TUTORIALS_DIR}/remote_scan_tutorial/RemoteScanTutorial.ipynb"
}

# Notebook Testing:
# Most notebook examples are have independent folders with only a single notebook, and most can be run in the same
# environment. To support more complex scenarios notebooks are split into (3) groups - independent notebooks,
# multipart examples, and notebooks that need a separate conda environment

# Examples involving multiple notebooks explicit order
MULTIPART_NOTEBOOKS=(patient_readmission data_statistics)

# Examples requiring a new conda env or new dependencies
NOTEBOOKS_REQUIRING_ENV_SETUP=(azureml_model_headers_demo sagemaker target_encoded xgboost-model)

# Example notebook folders to skip (usually empty). Useful in avoiding
# recomputes when a notebook bombs whilst running the script.
EXCLUDE_SINGULAR_NOTEBOOK=()

function testNotebooks() {
  cd "${NOTEBOOK_DIR}"
  _installAutomatedDeps
  runIndependentNotebooks
  runMultipartNotebooks
  if [ "${RUN_REMOTE_EXAMPLES}" = true ]; then
    echo "****************************************"
    echo "Running remote examples"
    echo "****************************************"
    runNotebooksWithEnvSetup
  else
    echo "Skipping remote examples..."
  fi
}

function _installAutomatedDeps() {
  conda install jupyter nbconvert -y
  pip install category_encoders
}

function _runNotebookInPlace() {
  # FYI - stdout/stderr from the notebook is NOT redirected by nbcovert (if needed check the log file at "~/.certifai")
  # An alternative would be to use papermill, however this requires (input notebook, CWD, output notebook), and doesn't
  # work well with wildcards.
  #   > pip install papermill
  #   > papermill --cwd $2 --log-output --request-save-on-cell-execute $1 $3
  jupyter nbconvert --to notebook --inplace --execute "$1"
}

function _convertNotebookToMarkdown() {
  jupyter nbconvert --to markdown "$1"
}

function runMultipartNotebooks() {
  # data_statistics
  _runNotebookInPlace "${NOTEBOOK_DIR}/data_statistics/prep_adult_data_drift.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/data_statistics/adult_drift_data_statistics.ipynb"

  # patient_readmission
  _runNotebookInPlace "${NOTEBOOK_DIR}/patient_readmission/patient-readmission-train.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/patient_readmission/patient-readmission-explain-scan.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/patient_readmission/patient-readmission-explain-results.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/patient_readmission/patient-readmission-trust-scan.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/patient_readmission/patient-readmission-trust-results.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/patient_readmission/patient-readmission-sampling-scan.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/patient_readmission/patient-readmission-sampling-results.ipynb"
}

function runIndependentNotebooks() {
  local multipart_grep
  multipart_grep="${MULTIPART_NOTEBOOKS[*]/#/-e }"

  local env_grep
  env_grep="${NOTEBOOKS_REQUIRING_ENV_SETUP[*]/#/-e }"

  local exclude_grep
  exclude_grep="${EXCLUDE_SINGULAR_NOTEBOOK[*]/#/-e }"

  # All examples with independent notebooks
  local notebooks
  # shellcheck disable=SC2086
  notebooks=$(ls "${NOTEBOOK_DIR}" | grep -v -e README -e datasets -e definitions -e utils ${multipart_grep} ${env_grep} ${exclude_grep})

  # shellcheck disable=SC2068
  for n in ${notebooks[@]}; do
    _runNotebookInPlace "${n}/*.ipynb"
  done
}

function runNotebooksWithEnvSetup() {
  _xgboostModel
  _targetEncodedAzuremlNotebook
  _azuremlModelHeadersDemo
  _sagemakerNotebook
}

function _azuremlModelHeadersDemo() {
  # Source azure credentials as env variables (the `shellcheck source` below ignores warnings from the dynamic path),
  # the notebooks expects `AML_USE_SP_AUTH`, `AML_TENANT_ID`, `AML_PRINCIPAL_ID`, and `AML_PRINCIPAL_PASS` to be set.
  # shellcheck source=/dev/null.
  source "${AZURE_ENV_FILE}"
  echo "resource_group: ${CERTIFAI_AZURE_DEV_RESOURCE_GROUP}"
  echo "subscription_id: ${CERTIFAI_AZURE_DEV_SUBSCRIPTION}"
  echo "workspace_name: ${CERTIFAI_AZURE_DEV_WORKSPACE_NAME}"

  # write config.json
  echo "{\"subscription_id\": \"${CERTIFAI_AZURE_DEV_SUBSCRIPTION}\", \"resource_group\": \"${CERTIFAI_AZURE_DEV_RESOURCE_GROUP}\", \"workspace_name\": \"${CERTIFAI_AZURE_DEV_WORKSPACE_NAME}\"}" >  "${NOTEBOOK_DIR}/azureml_model_headers_demo/config.json"

  # azureml_model_headers_demo
  cd "${NOTEBOOK_DIR}"
  conda remove -n certifai-azure-model-env --all -y
  conda env create -f "${NOTEBOOK_DIR}/azureml_model_headers_demo/certifai_azure_model_env.yml"
  conda activate certifai-azure-model-env
  # export variable so the toolkit from pipeline artifacts are picked up during installation
  TOOLKIT_WORK_DIR="${ARTIFACTS_DIR}/toolkit" _runNotebookInPlace "${NOTEBOOK_DIR}/azureml_model_headers_demo/part_one_installing_dependencies.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/azureml_model_headers_demo/german_credit_azure_ml_demo.ipynb"
  conda deactivate
}

function _targetEncodedAzuremlNotebook() {
  # Source azure credentials as env variables (the `shellcheck source` below ignores warnings from the dynamic path),
  # the notebooks expects `AML_USE_SP_AUTH`, `AML_TENANT_ID`, `AML_PRINCIPAL_ID`, and `AML_PRINCIPAL_PASS` to be set.
  # shellcheck source=/dev/null.
  source "${AZURE_ENV_FILE}"
  echo "resource_group: ${CERTIFAI_AZURE_DEV_RESOURCE_GROUP}"
  echo "subscription_id: ${CERTIFAI_AZURE_DEV_SUBSCRIPTION}"
  echo "workspace_name: ${CERTIFAI_AZURE_DEV_WORKSPACE_NAME}"

  # write config.json
  echo "{\"subscription_id\": \"${CERTIFAI_AZURE_DEV_SUBSCRIPTION}\", \"resource_group\": \"${CERTIFAI_AZURE_DEV_RESOURCE_GROUP}\", \"workspace_name\": \"${CERTIFAI_AZURE_DEV_WORKSPACE_NAME}\"}" >  "${NOTEBOOK_DIR}/target_encoded/certifai_multiclass_example/config.json"

  # target_encoded
  conda remove -n certifai-azure-model-env --all -y
  conda env create -f "${NOTEBOOK_DIR}/target_encoded/certifai_multiclass_example/certifai_azure_model_env.yml"
  conda activate certifai-azure-model-env
  installToolkit
  _runNotebookInPlace "${NOTEBOOK_DIR}/target_encoded/dataset_generation/german_credit_multiclass_dataset_generation.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/target_encoded/dataset_generation/german_credit_multiclass_dataset_encoding.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/target_encoded/certifai_multiclass_example/model_train_part1.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/target_encoded/certifai_multiclass_example/certifai_multiclass_evaluation_part2.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/target_encoded/certifai_multiclass_example/deploying_model_part3.ipynb"
  conda deactivate
}

function _sagemakerNotebook() {
  # Source aws credentials as env variables (the `shellcheck source` below ignores warnings from the dynamic path),
  # shellcheck source=/dev/null.
  source "${AWS_ENV_FILE}"
  pip install awscli
  aws configure set region us-east-1 --profile default
  aws configure set aws_access_key_id "${CERTIFAI_DEV_AWS_ACCESS_KEY}" --profile default
  aws configure set aws_secret_access_key "${CERTIFAI_DEV_AWS_SECRET_KEY}" --profile default
  aws configure set role_arn "${CERTIFAI_DEV_AWS_ROLE_ARN}" --profile default
  aws configure set source_profile default --profile default

  cd "${NOTEBOOK_DIR}"
  conda remove -n certifai-sagemaker-model-env --all -y
  conda env create -f "${NOTEBOOK_DIR}/sagemaker/certifai_sagemaker_model_env.yml"
  conda activate certifai-sagemaker-model-env
  # export variables so the toolkit from pipeline artifacts is used during installation
  TOOLKIT_WORK_DIR="${ARTIFACTS_DIR}/toolkit" _runNotebookInPlace "${NOTEBOOK_DIR}/sagemaker/part_one_installing_dependencies.ipynb"
  _runNotebookInPlace "${NOTEBOOK_DIR}/sagemaker/CertifaiSageMakerExample.ipynb"
  conda deactivate
}

function _xgboostModel() {
  # xgboost-model
  cd "${NOTEBOOK_DIR}"
  pip install "$XGBOOST_VERSION"
  _runNotebookInPlace "${NOTEBOOK_DIR}/xgboost-model/xgboostDmatrixExample.ipynb"
}

function main() {
  case ${1-local} in
   CI)
    setGlobals
    activateConda
    installToolkit
    _installModelRequirements
    _installLocalModelRequirements
    testAll
    rm -rf "${TOOLKIT_WORK_DIR}"
    ;;
   docker)
    setGlobals
    PUSH_IMAGES=true
    extractToolkit
    _installModelRequirements
    buildModelDeploymentImages
    ;;
   local-docker)
    setGlobals
    PUSH_IMAGES=false
    extractToolkit
    _installModelRequirements
    buildModelDeploymentImages
    ;;
   docker-builder)
    setGlobals
    PUSH_IMAGES=true
    extractToolkit
    _installModelRequirements
    buildPredictionServiceBaseImages
    ;;
   local-docker-builder)
    setGlobals
    PUSH_IMAGES=false
    extractToolkit
    _installModelRequirements
    buildPredictionServiceBaseImages
    ;;
   links)
    setGlobals
    activateConda
    testMarkdownLinks
    ;;
   models)
    setGlobals
    activateConda
    installToolkit
    _installModelRequirements
    _installLocalModelRequirements
    testModels
    ;;
   notebook)
    setGlobals
    activateConda
    installToolkit
    testNotebooks
    ;;
   tutorials)
    setGlobals
    activateConda
    installToolkit
    testTutorials
    ;;
   help)
    printHelp
    ;;
   *)
    printf "Unknown Option: %s\n" "$1"
    printHelp
    ;;
  esac
}
main "${1:-help}"
