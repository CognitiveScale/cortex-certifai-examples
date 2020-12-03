# Containerized Models test examples

This folder contains a test script and examples that can all be
containerized using the default prediction services.

The test script builds, runs and tests each of the examples in turn.

## H2O MOJO examples

h2o_auto_insurance - h2o mojo, regression
h2o_german_credit - h2o mojo, binary classification, infers metadata
h2o_iris - h2o mojo, multi-class, overrides MOJO outcome labels

## Python examples

sklearn_german_credit - sklearn, binary classification
xgboost_iris - XGBClassifier, multi-class classification
xgboost_dmatrix_income - xgboost with DMatrix, binary classification

## Test Setup

### Prerequisites

The following files must exist in this folder:
* license.txt - a valid H2O license file
* daimojo-xxx-linux_x86_64.whl - latest Driverless AI python mojo runtime
* certifai_toolkit/ - certifai toolkit v1.3.6 or above

The current conda environment has been setup with:
* python 3.6 (if 3.7 or 3.8, update PYTHON_VERSION in `run_test.sh`)
* pip install -U Jinja2

To train and test the models:
* Certifai toolkit installed in the current conda environment
* conda install -c conda-forge xgboost

To build/run the images: Docker

### Running the tests

To run the tests:
```
sh run_test.sh
```

The tests build four images, `h2o_mojo_predict`, `sklearn_predict`,  
`xgboost_predict` and `xgboost_dmatrix_predict`. These images can be
used with different metadata and model files to run different
models.

The prediction service images are run with the metadata.yml and model
artifact mounted from local filesystem, so that they can be run without remote
storage.  The same images could be run with metadata and models in remote
storage by changing the environment.yml.

The tests exit on any error, printing out the prediction service log
and deleting the running prediction service container.
