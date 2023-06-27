# How to create containerized models?

## Index
- [Pre-requisites](#pre-requisites)
- [Overview](#overview)
- [H2O Mojo Template](#h2o-mojo-template)
- [Python Template](#python-template)
- [Proxy Template](#proxy-template)
- [R Model Template](#r-model-template)


## [Pre-requisites](#pre-requisites)

- Certifai toolkit.
- A model (H2O MOJO pipeline or pickle).
- H2O MOJO runtime and license file (for running H2O MOJO models).
- A base docker image which has all the dependencies at the specific versions that were used when the model was trained.
- Locally installed:
    - To generate the template: python, PyYaml, Jinja2, and requirements-parser (`pip install -r requirements.txt`)
    - To build/run the image: Docker

## [Overview](#overview)

To generate the code templates for the existing model base images in [this repo](https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/scan-manager/docs/setup_artifacts/deployment):

  | Model-type | Generate command to run                                                                |
  |----------------------------------------------------------------------------------------| --- |
  | H2O Mojo | `./generate.sh -i certifai-model-container:latest -m h2o_mojo -f <path-to-toolkit>`    |
  | Python | `./generate.sh -i certifai-model-container:latest -m python -f <path-to-toolkit>`      |
  | Proxy | `./generate.sh -i certifai-proxy-container:latest -m proxy -f <path-to-toolkit>`       |
  | R | `./generate.sh -i  certifai-model-container:latest -m r_model -b rocker/r-apt:bionic -f <path-to-toolkit>` |

  Other commandline options:
  ```
% ./generate.sh --help                                                                                                                                                                                                                     31s
usage: ./generate.sh [options] [args]
Required:
	Target docker image to be built                          [-i | --target-docker-image]
	Certifai Toolkit path (unzipped directory)               [-t | --toolkit-path]
Optional:
	Model (.pkl) file path                                   [-l | --model]
	Requirements (requirements.txt) file path                [-f | --requirements-file]
	Prediction Service (prediction_service.py) file path     [-p | --prediction-service-file]
	Base docker image to be used to build the image          [-b | --base-docker-image]
	Directory to be created                                  [-d | --dir]
	Model type for template e.g h2o_mojo                     [-m | --model-type]
	Print help                                               [-h | --help]
  ```

  Each command will create a folder named `generated-container-model` in your current directory with the generated code
  for the containerization of your model. The template generated from the above commands is designed to work with
  standard [scikit-learn, XGBClassifier or XGBRegressor models](#python-template), [H2O MOJO](#h2o-mojo-template),
  and [R based models](#r-model-template).

  For an xgboost model using DMatrix, replace `-m python` with  `-m python_xgboost_dmatrix`.

  To specify the base docker image for your container, specify `-b <base-docker-image>` (Help for details)

  For additional `generate` options run:
  ```
  ./generate.sh --help
  ```

  Refer to the below sections for further instructions on containerizing your model.

## [H2O Mojo Template](#h2o-mojo-template)
### Step 1 - Template generation

Generate the code template for containerization of your model. Replace `certifai-model-container:latest`
with the image name and tag that you want to generate.
```
./generate.sh -i certifai-model-container:latest -m h2o_mojo -f <path-to-toolkit>
```
NOTE: When used in a CI/CD pipeline, we recommend generating a template
with a tag of `latest`. Each time you build the image, push both the latest tag
and a version tag to the docker repository.

The `generate` command will create a directory called `generated-container-model`
in your current directory with the generated code.

For more `generate` options:
```
./generate.sh --help
```

### Step 2 - Update the prediction service with information for your use case

Fill in the 'columns' field in the `metadata.yml` in the
`generated-container-model` folder. This field should identify the column names
of the data in the input instances that will be sent by Certifai.
This is the same as the columns in the evaluation dataset,
omitting outcome fields and any fields marked in the scan definition as "hidden".

The columns metadata is used in the
prediction service to transform the fields in the input instances to the
form that is expected by the model.

For a classification model, you should also fill in the 'outcomes' field.
This field is an array of the outcome values that should be returned
by the prediction service, in the order the probabilities are returned in
the results by the Mojo model. The values should be the same as the prediction
values in the Certifai scan definition. If these values are not provided, the
prediction service will attempt to infer them from the labels on the results
array.


### Step 3 - Test the prediction service running locally
When first setting up this template, you are recommended to test the
 prediction service by running it locally.

 1. Follow the instructions for the
 [H2O MOJO example](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/h2o_dai_german_credit) to setup the environment.

 2. Copy the MOJO and H2O license into the generated container folder:
 ```
 cp license.txt generated-container-model/license/license.txt
cp pipeline.mojo generated-container-model/model/pipeline.mojo
 ```

3. Run the service:
 ```
 python generated-container-model/src/prediction_service.py
 ```

 4. Test the service as described in the [H2O MOJO example](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/h2o_dai_german_credit)

### Step 4 - Copy daimojo dependencies
Copy the `daimojo` MOJO Python runtime `linux` dependency (`.whl` file) to `ext_packages` folder:

```
cp <path-to-linux-daimojo-file>.whl generated-container-model/ext_packages/
```

The file will be named something like `daimojo-2.4.8-cp37-cp37m-linux_x86_64.whl`

If you do not already have this package, you can download it from the H2O Driverless AI UI, see [instructions](http://docs.h2o.ai/driverless-ai/latest-stable/docs/userguide/scoring-pipeline-cpp.html#downloading-the-scoring-pipeline-runtimes).


### Step 5 - Build
Run the following command to build the prediction service docker image.

```
./generated-container-model/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i`
parameter (`certifai-model-container:latest` in this case).


### Step 6 - Configure cloud storage
Add respective cloud storage credentials, `MODEL_PATH` and `H2O_LICENSE_PATH` to
`generated-container-model/environment.yml` file. This will be used in the `RUN` step.

### Step 7 - Run
`Pre-requisite`: Make sure your model `.mojo` file and H2O license are placed at
the locations defined in `environment.yml` file.

Run the following command which would run the docker image using environment
variables from the environments file (`environment.yml`) that is being passed:

```
./generated-container-model/container_util.sh run
```

This will create a docker container running locally, with the prediction
service exposed on port 8551.

If you get an error such as:
```
FileNotFoundError: [Errno 2] No such file or directory: 'model/pipeline.mojo'
```
make sure you have configured the path to cloud storage and pushed your
model to that location.

### Step 8 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters,
or use Certifai to test the endpoint against a scan definition
`certifai definition-test -f scan_def.yaml`



## [Python Template](#python-template)
### Step 1 - Template generation

Generate the code template for containerization of your model:
```
./generate.sh -i certifai-model-container:latest -m python -f <path-to-toolkit>
```

This command should create a directory called `generated-container-model`
in your current directory with the generated code.

This template is designed to work with a standard scikit-learn model,
and with an XGBClassifier or XGBRegressor model. For an xgboost model using
DMatrix, use `-m python_xgboost_dmatrix`.

For more `generate` options:
```
./generate.sh --help
```

### Step 2 - Update the prediction service with information for your use case

The prediction service works out of the box with a standard scikit-learn model
and with an XGBClassifier or XGBRegressor model.

For other models, you may need to update the `set_global_imports` method in
`generated-container-model/src/prediction_service.py` to
import any required dependencies, and the `predict` and/or `soft_predict`
methods to predict using the model and return results in the expected
format.

If you are using `soft_predict` (e.g. for Shap), make sure `supports_soft_scoring: true`
is specified for the model in `generated-container-model/model/metadata.yml`
and in your scan definition.


### Step 3 - Test the prediction service running locally
When first setting up this template, you are recommended to test the
 prediction service by running it locally.

1.  Copy the model into the generated container folder:
 ```
 cp mymodel.pkl generated-container-model/model/model.pkl
 ```

2. Run the service:
 ```
 python generated-container-model/src/prediction_service.py
 ```

 3. Test the service by making a request to
 `http://127.0.0.1:8551/predict` with the respective parameters (see e.g.
   [app_test.py](../iris/app_test.py) in the iris example),
 or use Certifai to test the endpoint against your scan definition
 `certifai definition-test -f scan_def.yaml`


### Step 4 - Configure cloud storage
Add respective cloud storage credentials and `MODEL_PATH` to `generated-container-model/environment.yml` file. This will be used in the `RUN` step.

### Step 5 - Add extra-dependencies (optional)

The dependencies work out of the box with a standard scikit-learn model,
providing the model was trained with a version `1.0.2` of scikit-learn. If
you are using a different version, you should update
`generated-container-model/requirements.txt`.

If you are using xgboost or other models, you will need
to add relevant dependencies to `generated-container-model/requirements.txt`.

**Note**: dependencies are installed using `pip install`

### Step 6 - Build

```
./generated-container-model/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i`
parameter (`certifai-model-container:latest` in this case).

### Step 7 - Run
`Pre-requisite`: Make sure your model `.pkl` file is placed at the respective location defined in `environment.yml` file.

Run the following command which would run the docker image using environment variables from the environments file (`environment.yml`) that is being passed:

```
./generated-container-model/container_util.sh run
```

This should create a docker container and host the webservice.

### Step 8 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters,
or use Certifai to test the endpoint against a scan definition
`certifai definition-test -f scan_def.yaml`


## [Proxy Template](#proxy-template)
### Step 1 - Template generation

Generate the code template for containerization of your model:
```
./generate.sh -d generated-container-proxy -i certifai-proxy-container:latest -m proxy -f <path-to-toolkit>
```

This command should create a directory called `generated-container-proxy`
in your current directory with the generated code.

For more `generate` options:
```
./generate.sh --help
```

### Step 2 - Configure hosted model url
Add `HOSTED_MODEL_URL`  env variable to `generated-container-proxy/environment.yml` file. This will be used in the `RUN` step.

Optionally, add any additional auth/secret header token to above file. Don't forget to reference the same additional env variable in `src/prediction_service.py`

### Step 3 - Update request/response transformer methods inside src/prediction_service.py

- `transform_request_to_hosted_model_schema`: update this method to apply custom transformation to hosted model service request (/POST)
- `transform_response_to_certifai_predict_schema`: update this method to apply custom transformation on hosted model service response to transform to Certifai predict schema

**More info. available as docstring in `src/prediction_service.py`**

### Step 4 - Build
Run the following command to build the prediction service docker image.

```
./generated-container-proxy/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i` parameter (`certifai-proxy-container:latest` in this case).

### Step 5 - Run
Run the following command which would run the docker image using environment variables from the environments file (`environment.yml`) that is being passed:

```
./generated-container-proxy/container_util.sh run
```

This should create a docker container and host the webservice.

### Step 6 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters.

## [R Model Template](#r-model-template)
### Step 1 - Template generation

Generate the code template for containerization of your model:
```
./generate.sh -i  certifai-model-container:latest -m r_model -b rocker/r-apt:bionic -f <path-to-toolkit>
```

This command should create a directory called `generated-container-model`
in your current directory with the generated code.

Note: Value for `-m` option is `r_model` (by default)

For more `generate` options:
```
./generate.sh --help
```

### Step 2 - Configure Model Metadata
Provide list of column names in `columns` field in `metadata.yml` file located inside directory `generated-container-model/model`:

### Step 3 - Configure dependencies
- Add any binary dependencies to `requirements_bin.txt` e.g. `r-cran-randomforest`
- Add any other dependencies (whole prebuilt binary isn't available on r-cran) to `requirements_src.txt` e.g. `install.packages('custom-non-binary-package')`

**Note**: building binaries from source takes few minutes

### Step 4 - Configure prediction service
- For loading model dependencies add `library(packageName)` to file `src/prediction_service.R` e.g. `library(randomForest)` to load random forest package for prediction
- Model is assumed to be an `.rds` file. Persisted Model may contain additional functions and artifacts needed for data transformation at run-time. Supported list include
    - `encoder`: function to encode (scale etc.) incoming data. accessed using `model$encoder`
    - `artifacts`: an optional object that may be passed to encoder along with new data. accessed using `model$artifacts`

**Sample Usage**: `predict(model$model, newdata=model$encoder(test_data, model$artifacts))`. Refer to concrete example in `models/r-models`

### Step 5 - Configure cloud storage
Add S3 cloud storage credentials and `MODEL_PATH` to `generated-container-model/environment.yml` file. This will be used in the `RUN` step.

**Note**: When working with local models leave the `MODEL_PATH` empty and copy your `model.rds` file to directory `generated-container-model/model`

### Step 6 - Build
Run the following command to build the prediction service docker image.

```
./generated-container-model/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i` parameter (`certifai-model-container:latest` in this case).

### Step 7 - Run
`Pre-requisite`: Make sure your model `.rds` file is either

- placed at `model/model.rds`  or
- cloud storage and model path is configured in `environment.yml`


Run the following command which would run the docker image using environment variables from the environments file (`environment.yml`) that is being passed:

```
./generated-container-model/container_util.sh run
```

This should create a docker container that hosts the prediction service.

### Step 8 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters.
