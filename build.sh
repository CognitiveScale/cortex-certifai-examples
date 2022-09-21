#!/bin/bash -eux
#
##

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
PYTHON_VERSION="3.8"
ARTIFACTS_DIR="${SCRIPT_PATH}/artifacts"
TOOLKIT_PATH="${ARTIFACTS_DIR}/certifai_toolkit.zip"

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
  rm -rdf /tmp/toolkit/
  unzip -d /tmp/toolkit/ "${TOOLKIT_PATH}"
  cd /tmp/toolkit

  conda install --file requirements.txt -y
  pip install $(find /tmp/toolkit/packages/all -name cortex-certifai-common-*.zip)[s3,gcp,azure]
  pip install $(find /tmp/toolkit/packages/python${PYTHON_VERSION} -name cortex-certifai-engine-*.zip)[shap]
}

function build() {
  testModels
  testNotebooks
  testTutorials

  # TODO:
  #  1) build the containerized docker images for contents of 'templates/' check which are on the docs site first locally
  #  2) check to see if looks similar to the previous version images
  #  3) write pseudo logic for tagging the images
  #  4) Might need to update this docs page to mention latest examples are Python 3.8, not 3.6 - https://cognitivescale.github.io/cortex-certifai/docs/enterprise/scan-manager/scan-manager-setup#add-base-images
  #  5) Finish setting up and testing the pipeline
  #  6) Check with Prajna for setting up snyk scanning
  cd models/containerized_model
}

function buildLocal() {
  echo "TODO: build the containerized model - assume the toolkit located at toolkit dir"
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
# TODO(LA): Need to decide on versioning strategy - going with manual (explicit updates so far)
#VERSION=$(git describe --long --always --match='v*.*' | sed 's/v//; s/-/./')
GIT_SHA=$(git log -1 --pretty=%h)
VERSION="v4-${GIT_SHA}"
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