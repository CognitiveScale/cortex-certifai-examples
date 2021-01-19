# How to create containerized models?

## Index
- Pre-requisites
- H2O Mojo Template
- Python Template
- R Model Template

## [Pre-requisites](#pre-req)

- Certifai toolkit (from [CognitiveScale website](https://www.cognitivescale.com/try-certifai/)).
- A model (H2O MOJO pipeline or pickle).
- H2O MOJO runtime and license file (for running H2O MOJO models).
- A base docker image which has all the dependencies at the specific versions that were used when the model was trained.
- Locally installed:
    - To generate the template: python & Jinja2 (`pip install -U Jinja2`)
    - To build/run the image: Docker


## [H2O Mojo Template](#h2o-mojo-template)
### Step 1 - Template generation

Generate the code template for containerization of your model. Replace `certifai-model-container:latest`
with the image name and tag that you want to generate.
```
./generate.sh -i certifai-model-container:latest -m h2o_mojo
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
Define the dataset columns in `src/prediction_service.py` under the `COLUMNS`
variable. `COLUMNS` is expected to be a `list of strings`.

Note: The "outcome" column should not be included.

Fill in the `_get_prediction_class` in `src/prediction_service.py` to return
the appropriate class label for your model's outcomes.


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


### Step 4 - Copy Certifai packages
Copy the `packages` folder from inside the toolkit into the generated directory `generated-container-model`:

```
cp -r <certifai-toolkit-path>/packages generated-container-model/packages
```

NOTE: We copy the entire packages folder for convenience. Only the
`cortex-certifai-common` and `cortex-model-sdk` packages will be
built into the Docker image.

### Step 5 - Copy daimojo dependencies
Copy the `daimojo` MOJO Python runtime `linux` dependency (`.whl` file) to `ext_packages` folder:

```
cp <path-to-linux-daimojo-file>.whl generated-container-model/ext_packages/
```

The file will be named something like `daimojo-2.4.8-cp36-cp36m-linux_x86_64.whl`

If you do not already have this package, you can download it from the H2O Driverless AI UI, see [instructions](http://docs.h2o.ai/driverless-ai/latest-stable/docs/userguide/scoring-pipeline-cpp.html#downloading-the-scoring-pipeline-runtimes).


### Step 6 - Build
Run the following command to build the prediction service docker image.

```
./generated-container-model/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i`
parameter (`certifai-model-container:latest` in this case).


### Step 7 - Configure cloud storage
Add respective cloud storage credentials, `MODEL_PATH` and `H2O_LICENSE_PATH` to
`generated-container-model/environment.yml` file. This will be used in the `RUN` step.

### Step 8 - Run
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

### Step 9 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters,
or use Certifai to test the endpoint against a scan definition
`certifai definition-test -f scan_def.yaml`



## [Python Template](#python-template)
### Step 1 - Template generation

Generate the code template for containerization of your model:
```
./generate.sh -i certifai-model-container:latest
```

This command should create a directory called `generated-container-model`
in your current directory with the generated code.

Note: Value for `-m` option is `python` (by default)

For more `generate` options:
```
./generate.sh --help
```

### Step 2 - Copy artifacts
Copy the `packages` folder from inside the toolkit into the generated
directory `generated-container-model`:

```
cp -r <certifai-toolkit-path>/packages generated-container-model/packages
```

### Step 3 - Configure cloud storage
Add respective cloud storage credentials and `MODEL_PATH` to `generated-container-model/environment.yml` file. This will be used in the `RUN` step.

### Step 4 - Build
Run the following command to build the prediction service docker image.

```
./generated-container-model/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i` parameter (`certifai-model-container:latest` in this case).

### Step 5 - Run
`Pre-requisite`: Make sure your model `.pkl` file is placed at the respective location defined in `environment.yml` file.

Run the following command which would run the docker image using environment variables from the environments file (`environment.yml`) that is being passed:

```
./generated-container-model/container_util.sh run
```

This should create a docker container and host the webservice.

### Step 6 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters.


## [Proxy Template](#proxy-template)
### Step 1 - Template generation

Generate the code template for containerization of your model:
```
./generate.sh -d generated-container-proxy -i certifai-proxy-container:latest -m proxy
```

This command should create a directory called `generated-container-proxy`
in your current directory with the generated code.

For more `generate` options:
```
./generate.sh --help
```

### Step 2 - Copy artifacts
Copy the `packages` folder from inside the toolkit into the generated
directory `generated-container-proxy`:

```
cp -r <certifai-toolkit-path>/packages generated-container-proxy/packages
```

### Step 3 - Configure hosted model url
Add `HOSTED_MODEL_URL`  env variable to `generated-container-proxy/environment.yml` file. This will be used in the `RUN` step.

Optionally, add any additional auth/secret header token to above file. Don't forget to reference the same additional env variable in `src/prediction_service.py`

### Step 4 - Update request/response transformer methods inside src/prediction_service.py

- `transform_request_to_hosted_model_schema`: update this method to apply custom transformation to hosted model service request (/POST)
- `transform_response_to_certifai_predict_schema`: update this method to apply custom transformation on hosted model service response to transform to Certifai predict schema

**More info. available as docstring in `src/prediction_service.py`**

### Step 5 - Build
Run the following command to build the prediction service docker image.

```
./generated-container-proxy/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i` parameter (`certifai-proxy-container:latest` in this case).

### Step 6 - Run
Run the following command which would run the docker image using environment variables from the environments file (`environment.yml`) that is being passed:

```
./generated-container-proxy/container_util.sh run
```

This should create a docker container and host the webservice.

### Step 7 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters.

## [R Model Template](#r-template)
### Step 1 - Template generation

Generate the code template for containerization of your model:
```
./generate.sh -i  certifai-model-container:latest -m r_model -b rocker/r-apt:bionic
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
- Add any binary dependencies to `requirements_bin_R.txt` e.g. `r-cran-randomforest`
- Add any other dependencies (whole prebuilt binary isn't available on r-cran) to `requirements_src_R.txt` e.g. `install.packages('custom-non-binary-package')`

**Note**: building binaries from source takes few minutes

### Step 4 - Configure prediction service
- For loading model dependencies add `library(packageName)` to file `src/prediction_serivice.R` e.g. `library(randomForest)` to load random forest package for prediction 
- Model is assumed to be an `.rds` file. Persisted Model may contain additional functions and artifacts needed for data transformation at run-time. Supported list include
    - `encoder`: function to encode (scale etc.) incoming data. accessed using `model$encoder`
    - `artifacts`: an optional object that may be passed to encoder along with new data. accessed using `model$artifacts`

**Sample Usage**: `predict(model, newdata=model$encoder(test_data, model$artifacts))`. Refer to concrete example in `models/r-models`

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

This should create a docker container and host the webservice.

### Step 8 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters.