# How to create containerized models?

## Pre-requisites

- Certifai toolkit (from [CognitiveScale website](https://www.cognitivescale.com/try-certifai/)).
- A model (pickle) stored in a cloud storage (e.g Amazon S3).
- A base docker image which (strictly) simulates the trained model python environment.


## Step 1 - Template generation
TODO:
- This should ask for full docker base image path (and inject into the Dockerfile) and generate the code template


## Step 2 - Copy artifacts
Copy the `packages` folder from inside the toolkit to current directory (`containerized_model` in this case)

## Step 3 - Configure cloud storage
- Add respective cloud storage credentials and `MODEL_PATH` to `environment.yaml` file.

## Step 4 - Build and run
The following command would build the docker image and run it on port 8551.

```
./container_util.sh build && ./container_util.sh run
```

## Step 5 - Test
Make a request to `http://127.0.0.1/predict` with the respective parameters.
