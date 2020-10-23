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
./generate.sh <directory-name> <base-docker-image-name> <base-docker-image-tag>
```

This command should create a directory called `<director-name>` in your current directory with the generated code.

## Step 2 - Copy artifacts
Copy the `packages` folder from inside the toolkit into the generated directory `<directory-name>`.

## Step 3 - Configure cloud storage
Add respective cloud storage credentials and `MODEL_PATH` to `<directory-name>/environment.yaml` file. This will be used in the `RUN` step.

## Step 4 - Build
From inside the `<directory-name>` folder, run the following command which would build the docker image:

```
./container_util.sh build
```

## Step 5 - Run
From inside the `<directory-name>` folder, run the following command which would run the docker image using environment variables from the environments file (`environment.yml`) that is being passed:

```
./container_util.sh run ./environment.yml
```

This should create a docker container and host the webservice.

## Step 6 - Test
Make a request to `http://127.0.0.1/predict` with the respective parameters.
