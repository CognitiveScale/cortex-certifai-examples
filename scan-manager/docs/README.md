# Scan Manager Setup

Scan Manager provides Certifai users with an easy to use web-interface for configuring use cases and scans. Refer to the
[Cortex Certifai documentation](https://cognitivescale.github.io/cortex-certifai/docs/enterprise/scan-manager/use-scan-manager)
for more information on the Certifai Scan Manager.

This guide is for system administrators who are configuring Scan Manager to work with Certifai Enterprise on a Kubernetes cluster.

This document walks you through:

1. Obtaining the setup artifacts (templates etc).
2. Creating and pushing different model-type base images to your private registry.
3. Adding the base images to templates.

## Index

- [Pre-requisites](#pre-requisites)
  - [Templates and Files](#templates-and-files)
- [Setup](#setup)
  - [Using default artifacts](#using-default-artifacts)
  - [Creating base-images](#creating-base-images)
  - [Adding base images](#adding-base-images)
  - [Updating base images](#updating-base-images)
  - [Adding templates](#adding-templates)
  - [Deploying prediction service to a different namespace](#deploying-prediction-service-to-a-different-namespace)
  - [Kubernetes Setup](#kubernetes-setup)

## [Pre-requisites](#pre-requisites)

- An instance of Cortex Certifai Enterprise has been deployed and is running on Kubernetes with access to the container
  registry configured for use with that cluster. Installation instructions can be found
  [here](https://cognitivescale.github.io/cortex-certifai/docs/enterprise/installation/kubernetes-installation).
- The remote object storage (S3/GCS/Azure) URI path where Certifai Scan Manager's configuration files exist, for your
  Cortex Certifai deployment.
- A CLI client for uploading files to remote storage. This can either be
  the [Minio CLI client](https://min.io/docs/minio/linux/reference/minio-mc.html?ref=docs)
  for S3/GCS connections, or the [Azure CLI client](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) if
  you are you using Azure Blob Storage.
- (Optional) Custom model deployment artifacts for the Certifai Scan Manager. Example artifacts are included in
  the `setup_artifacts/` folder and are described in further detail below.

### [Templates and Files](#templates-and-files)

This section describes the list of available editable Scan Manager templates and .yaml files that you use to set up Certifai Scan Manager.

The templates define the set of model types available in Scan Manager. Each model type will have an associated .yaml
template file used to deploy the model in the Kubernetes, as well as a list of possible base images. The default
artifacts include deployment templates and .yaml config file(s); and are provided inside the `setup_artifacts/` folder.

The `deployment` folder contains:
- Deployment templates: `.yaml` templates that provide the configuration templates for deploying each of the specified model types on Kubernetes:
    - `python`: Uses a `python3.8` base image with `scikit-learn` pre-installed.
    - `h2o_mojo`: Uses a `python3.8` base image with `daimojo-2.4.8-cp36` whl pre-installed.
    - `r_model`: Uses `rocker/r-ver:latest` base image with `r-cran-randomforest` pre-installed.
    - `hosted_model`: Uses a `python3.8` base image for wrapping an already hosted model service.
- `config.yml`: A .yaml file that lists discoverable model types (from above) along with corresponding base images. A
  given model type can have more than one base image; this can be useful for managing conflicting dependencies.

The `files` folder contains additional files required to invoke your model. For example, you should include a
`license.txt` file if you are working with a h2o driver-less AI model.

The `k8s_definitions` folder contains:
- `scan-manager-configmap.yaml`: This file is used to configure Kubernetes parameters like [scan concurrency](https://cognitivescale.github.io/cortex-certifai/docs/toolkit/cli-usage/remote-scan-management#concurrency-value), [cpu, and memory resource requests](https://cognitivescale.github.io/cortex-certifai/docs/toolkit/cli-usage/remote-scan-management#required-cpu-and-memory).

## [Setup](#setup)

The below steps list the high level steps for setting up the Scan Manager artifacts. Refer to the below sections for
more details, as well as the [Cortex Certifai documentation](https://cognitivescale.github.io/cortex-certifai/docs/enterprise/scan-manager/scan-manager-setup).
If you only intend on using the default artifacts, then refer to [these instructions](#using-default-artifacts) instead.

1. [Create and push base images](#creating-base-images) to the container registry configured for use with your cluster.
  These base images will be used for working with different model types (e.g. scikit, h2o, r, proxy).
1. [Add the base image](#adding-base-images) created from the previous step to a model type in the `config.yaml` file. A
  default `config.yaml` is provided inside the `setup_artifacts/deployment` directory for initial setup.
1. [Add a deployment template](#adding-templates) file to the `setup_artifacts/deployments/` directory for a given model
  type.
1. (Optional) Make sure to update the `license.txt` file for h2o-mojo in the `setup_artifacts/files` directory, if you
  are working with `h2o-mojo` models.
1. Upload the Certifai Scan Manager setup artifacts to the object storage dedicated to the Certifai Scan Manager. Scripts
  are provided in the `setup_artifacts/` directory for uploading these artifacts.

  * If you are using an S3 compatible object storage, then run the following command from the `setup_artifacts/`
    directory. The script assumes the
    [Minio CLI client](https://min.io/docs/minio/linux/reference/minio-mc.html?ref=docs) is installed.
    ```commandline
    bash upload_artifact.sh <END_POINT> <ACCESS_KEY> <SECRET_KEY> <BUCKET_NAME>
    ```

    **Example**
    ```commandline
    bash upload_artifact.sh https://s3.amazonaws.com SOMEACCESSKEY SOMESECRETKEY BUCKETNAME
    ```

    For mode details run: `bash upload_artifact.sh -h`. **NOTE**: The `BUCKET_NAME` is the same bucket configured in the
    S3 URL used when you installed Scan Manager.

  * If you are using Azure blob storage, then run the following command from the `setup_artifacts/` directory. The
    script assumes the [Azure CLI client](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) is installed.
    ```commandline
    bash upload_artifact_azure.sh <CONTAINER_NAME> <DESTINATION_PATH> <ACCOUNT_NAME> <SAS_TOKEN>
    ```

    **Example**
    ```commandline
    bash upload_artifact_azure.sh certifai-container custom/path myaccount "sp=racwdl&st=2022-04-22T15:50:58Z&se=2022-05-02T22:54:58Z&spr=https&sv=2021-06-08&SR=c&sig=w2%2IycGHD%2Cdj0OyNlaEJ83RkpGR%2Fuu6qa7y60bX8lCnw%3D"
    ```

    For mode details run: `bash upload_artifact_azure.sh -h`. **NOTE**: The `SAS_TOKEN` is
    a [shared access signature (SAS)](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)
    that grants access to Azure storage container, and it wrapped in quotes in the example to avoid any word-splitting
    or character expansion.
1. Follow the [Kubernetes Setup](#kubernetes-setup) instructions to complete the Scan Manager setup.
1. Use the Certifai Scan Manager application to create use-cases and run scans.

### [Using Default Artifacts](#using-default-artifacts)

If you intend to use the default artifacts available under `setup_artifacts/` for setting up the Scan Manager without
creating any new bases images, then you should:
1. Ensure the Docker images included in the `setup_artifacts/deployment/config.yml` exist in the container registry
  configured for use with Certifai Enterprise. If you need to copy the images to your container registry:
   - Pull the Docker images listed in the `config.yml` from Dockerhub.

     Example:
     ```commandline
     docker pull c12e/cortex-certifai-model-scikit:v4-1.3.15-91-g57d0d29d
     ```
   - Tag the image, so it can be pushed to your container registry.

     Example:
     ```commandline
     docker tag c12e/cortex-certifai-model-scikit:v4-1.3.15-91-g57d0d29d  gcr.io/certifai/cortex-certifai-model-scikit:v4-1.3.15-91-g57d0d29d
     ```
  - Push the image to your container registry.

     Example:
     ```commandline
     docker push gcr.io/certifai/cortex-certifai-model-scikit:v4-1.3.15-91-g57d0d29d
     ```
2. Follow steps (4) to (7) in the [setup](#setup) instructions to be finish the setup.


### [Creating base images](#creating-base-images)

Base images are containers with pre-installed dependencies required to run model predict as a service. To create base
images for the above templates:

- Follow the instructions to
  [generate a template](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model#step-1---template-generation-1).
  This will create a template directory structure for a specific model type.
- Copy the Certifai Certifai toolkit packages (required) and any additional packages to the template directory created
  in the previous step, as
  described [here](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model#step-2---copy-artifacts)
- Follow the instructions
  to [build the base image](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model#step-7---build)
  for your model type.
- [Push the image](https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/models/containerized_model/DEPLOYMENT.md#step-1---push-image-to-registry-private)
  to the private registry configured for use with your cluster.
  - Make sure you have write-access to the registry and that you are authenticated to it.
    - Tag the Docker image.
      ```
      docker tag <docker-image> <your-private-registry-url>:<docker-image-with-tag>
      ```
    - To push the image to your private Docker registry run:
      ```
      docker push <your-private-registry-url>:<docker-image-with-tag>
      ```
      Your private registry must be accessible to the deployed instance of Certifai Scan Manager.

**NOTE**: The private registry must be accessible to the deployed instance of Certifai Scan Manager.

**NOTE**: To deploy the prediction service outside of scan manager set cloud storage credentials, `MODEL_PATH`, and (if
    needed) `H2O_LICENSE_PATH` in the `generated-container-model/environment.yml` file.

### [Adding base images](#adding-base-images)

To add base image of a new model type:

1. Create new base image following the instructions above.
2. Update the `config.yml`as follows:

- Add a new model type item (e.g. `pytorch_1.8`).
- Add a `<model_type>.deployment` field with the corresponding deployment template name (
  e.g. `pytorch_1.8_deployment.yml`).
- Create the `pytorch_1.8_deployment.yml` file in the same directory.
- Add a `<model_type>.default_base_image.name` field with human-readable name (`pytorch_1.8`).
- Add a `<model_type>.default_base_image.value` field with the fully qualified name of the image pushed above.
- Update the list of `<model_type>.available_base_images` with the same image value.

**Example**

  ```yaml
  pytorch_1.8:
    deployment: pytorch_1.8_deployment.yml
    default_base_image:
      name: pytorch_1.8
      value: gcr.io/certifai-dev/certifai-pytorch-container:tag
    available_base_images:
      - name: pytorch_1.8
        value: gcr.io/certifai-dev/certifai-pytorch-container:tag
  ```

To add a base image to an existing model type update the list of `<model_type>.available_base_images` with the newly
added base image.

### [Updating base-images](#updating-base-images)

To update base image of a given model type:

1. Create a new base image. (Follow the instructions above.)
2. Update the values for `<model_type>` in the `config.yml` including:

- `default_base_image.value`: with the fully qualified name of the image pushed above
- The corresponding name-value item pair list `available_base_images.value`: with the fully qualified name of the image
  pushed above

### [Adding templates](#adding-templates)

You can create and upload additional templates to your dedicated object storage any time.

**NOTE**: Containerized models must be compatible with the configured prediction service image in two ways:
- The model artifact must work with the installed library versions for the selected model type and image.

  For example, the default scikit prediction service image includes a specific version of scikit-learn, pandas, and numpy. However, each installation may have its own model type and images. Your MLOps team can provide this information.

- The way the model has been saved to file must be compatible with the way the prediction service loads it.

  For example, the default python prediction service images provided with Certifai expect the model to have been saved as a dictionary using code similar to:
    ```
    import pickle

    model_obj = {
       'model': dtree,
       # If the model does its own encoding, you can omit the encoder below
       'encoder': encoder
    }
    with open('dtree_model.pkl', 'wb') as file:
       pickle.dump(model_obj, file)
  ```

To create a new template to correspond with a new model type refer to the [template creation instructions](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model).

To use an existing template for a new model_type:

1. Copy a similar template from the [setup_artifacts directory](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/scan-manager/docs/setup_artifacts/)
2. Rename it to reflect the model type.
3. Add or update environment variables that the model service deployment requires. Environment variables are injected when a service is deployed.
4. Update `<model_type>.deployment` value in `config.yml` file (described [here](/enterprise/scan-manager/scan-manager-setup.md#add-base images)) to the filename you created above. ([config.yml example](https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/scan-manager/docs/setup_artifacts/deployment/config.yml))
5. Save the file to your local version of the templates and files. Keep the deployment file and template file in the same directory.
6. Use the shell script `bash upload_artifact.sh <END_POINT> <ACCESS_KEY> <SECRET_KEY> <BUCKET_NAME>` to upload the new template to your Scan Manager registry (`<AWS_BUCKET>`).
7. Add the corresponding base images to the registry. (Follow instructions below.)

Refer to the [guide on Model Secrets](https://cognitivescale.github.io/cortex-certifai/docs/enterprise/model-secrets).

### [Deploying prediction service to a different namespace](#deploying-prediction-service-to-a-different-namespace)

We recommend using a different namespace for your model deployment. <br>

To deploy prediction services to a different namespace (for admins only):

- Update or add the `deployment-namespace` field in `certifai-scan-manager` `ConfigMap` in the current namespace as
  follows: `deployment-namespace: <deployment-namespace>`
- Create Kubernetes secrets with the credentials for the remote object storage (S3/GCS/Azure) in the different
  namespace.

  **Example**: If you are using S3, then create secrets using following commands:
  ```
  kubectl create secret generic s3-bucket-access-key --from-literal=accesskey=<BUCKET_ACCESS_KEY> -n <deployment-namespace>
  kubectl create secret generic s3-bucket-secret-key --from-literal=secretkey=<BUCKET_SECRET_KEY> -n <deployment-namespace>
  ```

  **Example**: If you are using Azure, then create secrets using the following commands:
  ```
  kubectl create secret generic az-blob-account-name --from-literal=accountname=<ACCOUNT_NAME> -n <deployment-namespace>
  kubectl create secret generic az-blob-account-key --from-literal=accountkey=<ACCOUNT_KEY> -n <deployment-namespace>
  kubectl create secret generic az-blob-sas-token --from-literal=token=<SAS_TOKEN> -n <deployment-namespace>
  ```

- Create role and rolebinding in the new namespace as follows:
  Save the following snippet to file and call it `deployment-namespace-roles.yaml`
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: certifai-deployment
  namespace: <deployment-namespace>
rules:
  - apiGroups: [ "apps" ]
    resources: [ "deployments" ]
    verbs: [ "list", "get" , "patch", "create" ]
  - apiGroups: [ "" ]
    resources: [ "services" ]
    verbs: [ "list", "get", "patch", "create" ]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: certifai-scan-manager
  namespace: <deployment-namespace>
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: certifai-deployment
subjects:
  - kind: ServiceAccount
    name: certifai-scan-manager
    namespace: <current-namespace>

```

Edit `namespace` fields in the above snippet as needed.

- `<current-namespace>`: Name of the current namespace in which certifai is installed in.
- `<deployment-namespace>`: Name of the deployment namespace.

- Apply the file:
  ```
  kubectl apply -f deployment-namespace-roles.yaml -n <deployment-namespace>
  ```

Now, creating a new usecase with Scan Manager will create prediction services in `<deployment-namespace>` namespace.

### [Kubernetes Setup](#kubernetes-setup)

To configure Scan Manager:

1. Create a Kubernetes `ConfigMap` using `setup_artifacts/k8s_definitions/scan-manager-configmap.yaml` file as a
   template.

2. In the file set the following:

`scan-config` - These settings provide configuration for parallel scanning (scan concurrency), cpu, and memory. You may
also specify use case level configurations for these properties.

`deployment-namespace` - namespace used to deploy models, **NOTE**: Scan manager will default the `deployment-namespace`
to the Kubernetes namespace Certifai is running in, if not set.

**Example**
  ```yaml
  scan-config:
    default:
      parallel: 1
      cpu-req: "1000m"
      mem-req: "500Mi"
      usecase:
        <usecase_id>:
          parallel: 2
          cpu-req: "1000m"
          mem-req: "500Mi"
  deployment-namespace: certifai
  ```

3. To apply the default Scan Manager `ConfigMap` use following command.

  ```bash
  kubectl apply -f setup_artifacts/k8s_definitions/scan-manager-configmap.yaml -n <NAMESPACE>
  ```

- Secret Configuration

Save object storge credentials to Kubernetes secrets.

**Example**: If you are using S3, then create secrets using following commands:

  ```
  kubectl create secret generic s3-bucket-access-key --from-literal=accesskey=<BUCKET_ACCESS_KEY> -n <NAMESPACE>
  kubectl create secret generic s3-bucket-secret-key --from-literal=secretkey=<BUCKET_SECRET_KEY> -n <NAMESPACE>
  ```

**Example**: If you are using Azure, then create secrets using the following commands:

  ```
  kubectl create secret generic az-blob-account-name --from-literal=accountname=<ACCOUNT_NAME> -n <NAMESPACE>
  kubectl create secret generic az-blob-account-key --from-literal=accountkey=<ACCOUNT_KEY> -n <NAMESPACE>
  kubectl create secret generic az-blob-sas-token --from-literal=token=<SAS_TOKEN> -n <NAMESPACE>
  ```

Kubernetes secrets are injected as `valueFrom` environment variables when the service is deployed.
