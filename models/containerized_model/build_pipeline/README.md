# Containerized Models build pipeline example

This folder contains a build script that illustrates how to build images
for models with different prediction service source code.

The build script takes two parameters:
* the service name (e.g. h2o_german_credit)
* the model type (h2o_mojo, python_sklearn)

There should be a `<service_name>` folder for each prediction service to be
built, containing `src/prediction_service.py`.

The script builds an image `<prefix><model_name>:latest` e.g.
`c12e/h2o_german_credit:latest` and also tags it with a git SHA. Update the
script to set the appropriate prefix for your organization's docker repository.

### Prerequisites

The following files must exist in this folder:
* license.txt - a valid H2O license file
* daimojo-xxx-linux_x86_64.whl - Driverless AI python mojo runtime
* certifai_toolkit/ - certifai toolkit v1.3.6 or above

The current conda environment has been setup with:
* python 3.6 (if 3.7 or 3.8, update PYTHON_VERSION in `run_test.sh`)
* pip install -U Jinja2


### Build the image

To run the build for the example MOJO model prediction service:
```
sh run_build.sh h2o_german_credit h2o_mojo
```

To run the build for the example sklearn model prediction service:
```
sh run_build.sh sklearn_german_credit python-sklearn
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
