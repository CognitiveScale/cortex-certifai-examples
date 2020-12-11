# How to create containerized models?

## Index
- Pre-requisites
- H2O Mojo Template
- Python Template


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
./generate.sh -i certifai-model-container:latest -m python
```

This command should create a directory called `generated-container-model`
in your current directory with the generated code.

This template is designed to work with a standard scikit-learn model,
and with an XGBClassifier or XGBRegressor model. For an xgboost model using
DMatrix, use `-m python-xgboost-dmatrix`.

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


### Step 4 - Copy artifacts
Copy the `packages` folder from inside the toolkit into the generated
directory `generated-container-model`:

```
cp -r <certifai-toolkit-path>/packages generated-container-model/packages
```

### Step 5 - Configure cloud storage
Add respective cloud storage credentials and `MODEL_PATH` to `generated-container-model/environment.yml` file. This will be used in the `RUN` step.

### Step 6 - Add extra-dependencies (optional)

The dependencies work out of the box with a standard scikit-learn model,
providing the model was trained with version 0.23.2 of scikit-learn. If
you are using a different version, you should update
`generated-container-model/requirements.txt`.

If you are using xgboost or other models, you will need
to add relevant dependencies to `generated-container-model/requirements.txt`.

**Note**: dependencies are installed using `pip install`

### Step 7 - Build

```
./generated-container-model/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i`
parameter (`certifai-model-container:latest` in this case).

### Step 8 - Run
`Pre-requisite`: Make sure your model `.pkl` file is placed at the respective location defined in `environment.yml` file.

Run the following command which would run the docker image using environment variables from the environments file (`environment.yml`) that is being passed:

```
./generated-container-model/container_util.sh run
```

This should create a docker container and host the webservice.

### Step 9 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters,
or use Certifai to test the endpoint against a scan definition
`certifai definition-test -f scan_def.yaml`
