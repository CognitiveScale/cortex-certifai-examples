# Containerized Models build pipeline example

This folder contains a build script that illustrates how to build images
for models with different prediction service source code.

The build script takes two parameters:
* the model type (h2o_mojo, python_sklearn)
* the model name (e.g. sklearn_german_credit)

It builds an image `<model_name>:latest`. When used in a real pipeline,
you will want to extend this script to tag with a gitsha and push to docker
registry.

### Prerequisites

The following files must exist in this folder:
* license.txt - a valid H2O license file
* daimojo-xxx-linux_x86_64.whl - Driverless AI python mojo runtime
* certifai_toolkit/ - certifai toolkit v1.3.6 or above

The current conda environment has been setup with:
* python 3.6 (if 3.7 or 3.8, update PYTHON_VERSION in `run_test.sh`)
* pip install -U Jinja2


### Build the image

To run the build:
```
sh run_build.sh h2o_german_credit h2o_mojo
```

### Run the prediction service locally

Either setup the model artifact and license file in s3/minio and use
`./generated-container-model run` as in [the README](../README.md) or
setup files and mount them into the docker image as below.
```
cp pipeline.mojo generated-container-model/model/
cp license.txt generated-container-model/license
docker run -p 8551:8551 -v $(pwd)/generated-container-model/model:/model  \
  -v $(pwd)/generated-container-model/license:/license \
  --env-file generated-container-model/environment.yml \
  -t h2o_german_credit
```
