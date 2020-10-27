# How to create containerized models?

## Pre-requisites

- Certifai toolkit (from [CognitiveScale website](https://www.cognitivescale.com/try-certifai/)).
- A model (pickle) stored in a cloud storage (e.g Amazon S3).
- A base docker image which has all the dependencies at the specific versions that were used when the model was trained.
- Locally installed:
    - Docker
    - Jinja2 (`pip install -U Jinja2`)


## Step 1 - Template generation

Generate the code template for containerization of your model:
```
./generate.sh -i certifai-model-container:latest
```

This command should create a directory called `generated-container-model` in your current directory with the generated code.

For more `generate` options:
```
./generate.sh --help
```

## Step 2 - Copy artifacts
Copy the `packages` folder from inside the toolkit into the generated directory `generated-container-model`:

```
cp -r <certifai-toolkit-path>/packages generated-container-model/
```

## Step 3 - Configure cloud storage
Add respective cloud storage credentials and `MODEL_PATH` to `generated-container-model/environment.yaml` file. This will be used in the `RUN` step.

## Step 4 - Build
Run the following command to build the prediction service docker image.

```
./generated-container-model/container_util.sh build
```

This will create a docker image with name specified at `Step 1` with `-i` parameter (`certifai-model-container:latest` in this case).

## Step 5 - Run
`Pre-requisite`: Make sure your model `.pkl` file is placed at the respective location defined in `environment.yml` file.

Run the following command which would run the docker image using environment variables from the environments file (`environment.yml`) that is being passed:

```
./generated-container-model/container_util.sh run
```

This should create a docker container and host the webservice.

## Step 6 - Test
Make a request to `http://127.0.0.1:8551/predict` with the respective parameters.
