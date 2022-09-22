#!/bin/bash -eux
#
##

PUSH_IMAGES=false
SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
PYTHON_VERSION="3.8"
ARTIFACTS_DIR="${SCRIPT_PATH}/artifacts"
TOOLKIT_PATH="${ARTIFACTS_DIR}/certifai_toolkit.zip"
WORK_DIR="/tmp/toolkit"
PACKAGES_DIR="${WORK_DIR}/packages"
TEMPLATES_DIR="${SCRIPT_PATH}/models/containerized_model"

function activateConda(){
    set +u
    eval "$(conda shell.bash hook)"
    conda create -n certifai python="${PYTHON_VERSION}" -y
    conda activate certifai
    conda env list
    which python
    which pip
}

function installToolkit() {
  if [ ! -f "${TOOLKIT_PATH}" ]; then
    echo "Certifai toolkit (ZIP) not found found! Toolkit is expected to be at ${TOOLKIT_PATH}"
    exit 1
  fi
  local cwd="${PWD}"
  rm -rdf ${WORK_DIR}
  unzip -d ${WORK_DIR} "${TOOLKIT_PATH}"
  cd /tmp/toolkit

  conda install --file requirements.txt -y
  pip install $(find /tmp/toolkit/packages/all -name cortex-certifai-common-*.zip)[s3,gcp,azure]
  pip install $(find /tmp/toolkit/packages/python${PYTHON_VERSION} -name cortex-certifai-engine-*.zip)[shap]
  cd "${cwd}"
}

function getToolkitVersion() {
  echo $(grep 'Scanner' < "${WORK_DIR}/version.txt"  | cut -d ' ' -f 3)
}

function build() {
  PUSH_IMAGES=false
  test
  build_model_deployment_base_images
  # TODO:
  #  4) Might need to update this docs page to mention latest examples are Python 3.8, not 3.6 - https://cognitivescale.github.io/cortex-certifai/docs/enterprise/scan-manager/scan-manager-setup#add-base-images
  #  5) Finish setting up and testing the pipeline
  #  6) Check with Prajna for setting up snyk scanning
}

function buildLocal() {
  PUSH_IMAGES=false
  test
  build_model_deployment_base_images
}

function build_model_deployment_base_images() {
  _build_template "c12e/cortex-certifai-model-scikit:${VERSION}" python
  _build_template "c12e/cortex-certifai-model-h2o-mojo:${VERSION}" h2o_mojo
  _build_template "c12e/cortex-certifai-hosted-model:${VERSION}" proxy

   # TODO: The base image rocker/r-apt:bionic` is outdated, but the image fails to build when using
   # `rocker/r-ver:3.6.1` or `rocker/r-ver:latest` because `r-cran-aws.s3` is not found.
  _build_template "c12e/cortex-certifai-model-r:${VERSION}" r_model rocker/r-apt:bionic
}

function _build_template() {
  # $1 image
  # $2 model-type
  # $3 base-image (optional)
  local out_dir=/tmp/work
  rm -rdf "${out_dir}"
  cd "${TEMPLATES_DIR}"

  local base_image="${3:-}"
  if [ -z "$base_image" ]; then
    ./generate.sh --target-docker-image "$1" \
                --dir "${out_dir}" \
                --model-type "$2"
                # explicitly use default base image
  else
    ./generate.sh --target-docker-image "$1" \
                --dir "${out_dir}" \
                --model-type "$2" \
                --base-docker-image "${base_image}"
  fi

  cp -r "${PACKAGES_DIR}" "${out_dir}"
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
  testModels
  testNotebooks
  testTutorials
}

function testModels() {
  echo "TODO: automate subset of model examples"
  # for each
  # - train the models
  # - start the app in one process,
  # - run the test in another process
  # - assert both processes exit successfully
}

function testNotebooks() {
  echo "TODO: automate running subset of notebooks"
  # Use Either
  # - nbmake (https://github.com/treebeardtech/nbmake)
  # - nbval (https://github.com/computationalmodelling/nbval)
  # - testbook (https://testbook.readthedocs.io/en/latest/getting-started/index.html)
}

function testTutorials() {
  echo "TODO: automate running subset of tutorials"
  # Use Either
  # - nbmake (https://github.com/treebeardtech/nbmake)
  # - nbval (https://github.com/computationalmodelling/nbval)
  # - testbook (https://testbook.readthedocs.io/en/latest/getting-started/index.html)
}


### MAIN ####
# TODO(LA): Need to decide on versioning strategy for model templates, part of the trouble here is that template images
#  include the Certifai packages, so we should tag them in such a way to show that version.
#
# Current tagging strategy: `<version-counter>-<toolkit-version>`
#
#   `<version-counter>` is a running count we maintain based on Python version & other dependency versions
#
# Example: c12e/cortex-certifai-model-scikit:v3-1.3.11-120-g5d13c272
#
#VERSION=$(git describe --long --always --match='v*.*' | sed 's/v//; s/-/./')
CERTIFAI_VERSION=$(getToolkitVersion)
GIT_SHA=$(git log -1 --pretty=%h)
VERSION="v4-${CERTIFAI_VERSION}"
echo "##### BUILDING ${VERSION} ######"
case ${1-local} in
 CI*)
  activateConda
  installToolkit
  build
  ;;
*)
 buildLocal
 ;;
esac
