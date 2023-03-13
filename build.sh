#!/bin/bash -eu
#
##
set -eu

function setGlobals() {
  set -x
  PUSH_IMAGES=false
  SKIP_CONDA="${SKIP_CONDA:-false}"
  SKIP_TOOLKIT="${SKIP_TOOLKIT:-false}"
  PYTHON_VERSION="3.8"
  SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
  ARTIFACTS_DIR="${SCRIPT_PATH}/artifacts"
  TOOLKIT_PATH="${ARTIFACTS_DIR}/certifai_toolkit.zip"
  TOOLKIT_WORK_DIR="${ARTIFACTS_DIR}/toolkit"
  PACKAGES_DIR="${TOOLKIT_WORK_DIR}/packages"
  TEMPLATES_DIR="${SCRIPT_PATH}/models/containerized_model"
  NOTEBOOK_DIR="${SCRIPT_PATH}/notebooks"
  TUTORIALS_DIR="${SCRIPT_PATH}/tutorials"
  BUILD_REPORT="${ARTIFACTS_DIR}/buildReport.txt"
  BUILD_REPORT_JSON="${ARTIFACTS_DIR}/buildReport.json"
  AWS_ENV_FILE="${ARTIFACTS_DIR}/.aws_env"
  AZURE_ENV_FILE="${ARTIFACTS_DIR}/.azure_env"
}

function printHelp() {
  # The help message is defined outside of `setGlobals` to avoid echo-ing its value when running the script with -x flag
  local prog_name
  prog_name="$(basename "$0")"

  local usage
  usage="$prog_name [options...]

Build and test Certifai examples.

Options:
  CI
      Run all notebook, tutorial, and model examples

  docker
      Build and push base docker images for example Prediction Service templates (used by Scan Manager).

  local-docker
      Build base docker images for example Prediction Service templates (used by Scan Manager). Does not push to dockerhub.

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

function buildLocal() {
  PUSH_IMAGES=false
  test
  build_model_deployment_base_images
}


# We have to enforce a versioning strategy in the example model templates. Part of the trouble here is that template
# images install the Certifai packages, so we should tag them in such a way to show that version.
#
# Current tagging strategy: `<version-counter>-<toolkit-version>`
#
#   `<version-counter>` is a running count we maintain based on the base image, Python version, & other dependencies
#
# Example: c12e/cortex-certifai-model-scikit:v3-1.3.11-120-g5d13c272
function build_model_deployment_base_images() {
  local certifai_version
  certifai_version=$(getToolkitVersion)

  local version
  version="v4-${certifai_version}"
  echo "##### BUILDING ${version} ######"

  local scikit_image="c12e/cortex-certifai-model-scikit:${version}"
  local h2o_image="c12e/cortex-certifai-model-h2o-mojo:${version}"
  local proxy_image="c12e/cortex-certifai-hosted-model:${version}"
  local r_image="c12e/cortex-certifai-model-r:${version}"

  _build_template "${scikit_image}" python
  _build_template "${h2o_image}" h2o_mojo
  _build_template "${proxy_image}" proxy

   # TODO: The base image rocker/r-apt:bionic` is outdated, but the image fails to build when using
   # `rocker/r-ver:3.6.1` or `rocker/r-ver:latest` because `r-cran-aws.s3` is not found.
  _build_template "${r_image}" r_model rocker/r-apt:bionic

  echo "{\"scikit\": \"${scikit_image}\", \"h2o\": \"${h2o_image}\", \"proxy\": \"${proxy_image}\", \"r\": \"${r_image}\" }" > "${BUILD_REPORT_JSON}"
  printf "%s\n%s\n%s\n%s\n" "${scikit_image}" "${h2o_image}" "${proxy_image}" "${r_image}" > "${BUILD_REPORT}"
}

function _build_template() {
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

function test() {
  testMarkdownLinks
  testModels
  testNotebooks
  testTutorials
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
    npm install -g markdown-link-check
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
  echo "TODO: automate subset of model examples - "
  # for each
  # - train the models
  # - start the app in one process,
  # - run the test in another process
  # - assert both processes exit successfully
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
  runNotebooksWithEnvSetup
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
  pip install xgboost
  _runNotebookInPlace "${NOTEBOOK_DIR}/xgboost-model/xgboostDmatrixExample.ipynb"
}

function main() {
  case ${1-local} in
   CI)
    setGlobals
    activateConda
    installToolkit
    test
    rm -rf "${TOOLKIT_WORK_DIR}"
    ;;
   docker)
    setGlobals
    PUSH_IMAGES=true
    extractToolkit
    build_model_deployment_base_images
    ;;
   local-docker)
    setGlobals
    PUSH_IMAGES=false
    extractToolkit
    build_model_deployment_base_images
    ;;
   links)
    setGlobals
    activateConda
    testMarkdownLinks
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
