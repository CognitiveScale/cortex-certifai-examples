
# SCAN MANAGER SETUP  
  
## Index  
- [Pre-requisites](#pre-requisites)  
- [Default-Setup](#setup)  
- [Components](#components)  
- [Creating Base-Images](#creating-base-images)  
- [Adding Base-Images](#adding-base-images)  
- [Updating Base-Images](#updating-base-images)  
- [Adding templates](#adding-templates)  
- [Deploying Prediction Service to a different namespace](#deploying-prediction-service-to-a-different-namespace)
- [Kube Setup](#kube-setup)  

  
## [Pre-requisites](#pre-requisites)  
- Instance of Cortex Certifai deployed and running on kubernetes with access to container registry. Install instructions can be found [here](https://cognitivescale.github.io/cortex-certifai/docs/enterprise/installation/kubernetes-installation).
- Certifai Scan Manager data directory (object storage e.g. S3 Bucket)  
- Certifai Scan Manager artifacts:  
  - deployment  
  - files  
  
## [Setup](#setup)
- [Create and push base-images](#creating-base-images) to container registry for working with different model types (scikit, h2o, r etc.)
- [Add](#adding-base-images) the base-image created above to a model type
- Default `config.yaml` is provided inside `setup_artifacts/deployment` directory for initial setup
- [Add](#adding-templates) corresponding templates for the given model types and base-image
- Make sure to update the `license.txt` file for h2o-mojo in the `setup_artifacts/files` directory (when working with h2o-mojo models)
- Run the `sh upload_artifact.sh <END_POINT> <ACCESS_KEY> <SECRET_KEY> <BUCKET_NAME>` script from the `setup_artifacts` directory   
  to make the updated artifacts available for Scan Manager to get started[Minio Client should be installed before running sh upload_artifact.sh]
- `BUCKET_NAME` is the same bucket configured when installing Scan Manager
- Use the Scan Manager App UI to create use-cases and run scans

  
## [Components](#components) 
- This section describes the list of editable Scan Manager components
- Default components include deployment templates and config yaml(s) ; and are provided inside the `setup_artifacts` directory
- `deployment` : directory containing model deployment (as service) template yaml(s)  
  - `<my_model>_deployment.yml` : template yaml for deploying a given model type (my_model) where <my_model> could be any of scikit, r, h2o, xgboost etc.
  - `config.yml` : list of discoverable model deployment templates (from above) along with corresponding [base-images](#base-images)  
- `files` : directory additional files (e.g. license.txt) required to invoke for instance h2o driver-less ai model  
  
Deployment templates are related to model type by:  
 - packaging dependencies for a given model type (e.g. scikit-learn v0.23) in the base-image   
 - a given model type can have more than one base-image (useful for managing conflicting dependencies)  
 - template/base-image relationship is described using `config.yml`  
  
Default templates (along with corresponding config.yml) includes  
 - scikit_0.23: uses python3.6 base-image with scikit-learn v0.23 pre-installed  
 - h2o_mojo: uses python3.6 base-image with daimojo-2.4.8-cp36 whl pre-installed  
 - r_model: uses rocker/r-apt:bionic base image with r-cran-randomforest pre-installed 
-  hosted_model: uses python3.6 base-image wrap already hosted model services
  
## [Creating base-images](#creating-base-images)
[Base Images](#base-images) are containers with pre-installed dependencies required to run model predict as a service.
To create base-images for the above templates:  
 - follow instructions [generate-template](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model#step-1---template-generation-1)  
  to create a template directory structure for the given model type (e.g. python scikit)   
 - copy Cortex Certifai (required) and additional packages (optional) described in [copy-packages](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model#step-2---copy-artifacts)     
 - build the base-image using [build-base-image](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model#step-4---build)  
 - [push-built-image](https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/models/containerized_model/DEPLOYMENT.md#step-1---push-image-to-registry-private) to private registry  
  
**note**: above private registry must be accessible to the deployed instance of Certifai Scan Manager  
  
## [Adding base-images](#adding-base-images)  
To add base-image of a new model type:  
 - create new base-image using [creating-base-image](#creating-base-images)  
 - update `config.yml`:  
    - add a new model type item (e.g. pytorch_1.8)  
    - add `model_type_deployment` with the corresponding deployment template name (e.g. pytorch_1.8_deployment.yml  
      make sure to create the `pytorch_1.8_deployment.yml` file in the same directory  
    - add `model_type.default_base_image.name` with human-readable name (pytorch_1.8)  
    - add `model_type.default_base_image.value` with the fully qualified name of the image pushed above  
    - also update the list of `model_type.available_base_images` with the same image value
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
 
To add a base-image to an existing model type:  
 - update the list of `model_type.available_base_images` with the newly added base-image  
  
## [Updating base-images](#updating-base-images)  
To update base-image of a given model type:  
 - create new base-image using [creating-base-image](#creating-base-images)  
 - update values for `<model_type>` in `config.yml` :  
    - `default_base_image.value` : with the fully qualified name of the image pushed above  
    - corresponding name-value item pair in list `available_base_images.value` : with the fully qualified name of the image pushed above  
    
  
## [Adding templates](#adding-templates)  
  
To add a new deployment template corresponding to a new model type:  
 - create new template by copying a similar default template inside deployment directory and name it accordingly  
 - add/update any environment variable that model service deployment may require  
 - environment variables are injected when service is deployed. Refer to guide on scan manager secrets  
 - update `<model_type>.deployment` value in `config.yml` to the deployment filename created above  
 - make sure to [add-corresponding-base-images](#adding-base-images) to private registry  
 - refer to [template-creation](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model#python-template) docs for generating custom templates for different model types

## [Deploying prediction service to a different namespace](#multiple-namespace-support)

We recommend using a different namespace for your model deployment. <br>

To deploy prediction services to a different namespace (for admins only):
- Update/Add `deployment-namespace` field in `certifai-scan-manager` `ConfigMap` in the current namespace as follows:
    `deployment-namespace: <deployment-namespace>`
- Set S3-Bucket credentials (access and secret keys) to different namespace kube secrets.

Create secrets using following command
  ```
  kubectl create secret generic s3-bucket-access-key --from-literal=accesskey=<BUCKET_ACCESS_KEY> -n <deployment-namespace>
  kubectl create secret generic s3-bucket-secret-key --from-literal=secretkey=<BUCKET_SECRET_KEY> -n <deployment-namespace>
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

```text
Notes: 
- Edit `namespace` fields in the above snippet as needed.
- `<current-namespace>`: Name of the current namespace in which certifai is installed in.
- `<deployment-namespace>`: Name of the deployment namespace.
```

- Apply the file as:
`kubectl apply -f deployment-namespace-roles.yaml -n <deployment-namespace>`

Now, creating a new usecase with ScanManager would create prediction services in `<deployment-namespace>` namespace.

## [Kube Setup](#kube-setup)

- Scan Manager Configuration:


  Create a kube `ConfigMap` using `setup_artifacts/k8s_definitions/scan-manager-configmap.yaml` file

  using `setup_artifacts/k8s_definitions/scan-manager-configmap.yaml` file you can set 

  `scan-config` - set scan configuration like parallel(scan concurrency), cpu and memory, also you can specify use case level config

  `deployment-namespace` -  namespace used to deploy models,  Note: Scan manager will check if `deployment-namespace` is set or not. If not set (or not present), deployment namespace set to `NAMESPACE` env variable on startup.

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

  To apply default scan manager ConfigMap use following command

  ```bash
  kubectl apply -f setup_artifacts/k8s_definitions/scan-manager-configmap.yaml -n <NAMESPACE>
  ```

- Secret Configuration


  Save s3 bucket credentials (bucket access key and bucket secret key) to kube secrets using following commands
    ```bash
    kubectl create secret generic s3-bucket-access-key --from-literal=accesskey=<BUCKET_ACCESS_KEY> -n <NAMESPACE>
    kubectl create secret generic s3-bucket-secret-key --from-literal=secretkey=<BUCKET_SECRET_KEY> -n <NAMESPACE>
    ```
  
  kube secrets are injected as `valueFrom` envs when service is deployed

