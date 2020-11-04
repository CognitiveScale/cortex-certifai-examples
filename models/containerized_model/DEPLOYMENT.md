# How to deploy the "containarized" model to Kubernetes?

## Pre-requisites
- A Containerized model.
- `kubectl`.
- Private docker registry to push containerized image to.
- A valid `kubeconfig` file with the current context activated.

## Step 1 - Push image to registry (private)
The containerized image that has been built as part of `Pipeline 1` will need to be pushed to a private docker registry in order for the `k8s` cluster to pull it from.

### Pre-requisites
- Private docker registry to push containerized image to. This should be the registry that your`k8s` cluster is configured with.
- Make sure you have write-access to the registry and are authenticated.

### Tag docker image
```
docker tag <docker-image> <your-private-registry-url>:<docker-image-with-tag>
```

### Push the image
```
docker push <your-private-registry-url>:<docker-image-with-tag>
```

## Step 2 - Update deployment configuration and credentials
Update `MODEL_PATH`,  cloud storage credentials (e.g s3) and the `docker image` name in the `generated-container-model/deployment.yml` file.
Below is the snippet from `generated-container-model/deployment.yml` that needs to be updated:
```
spec:
  containers:
    - image: "<your-docker-image>"
      imagePullPolicy: IfNotPresent
      name: {{DEPLOYMENT_NAME}}
      ports:
        - containerPort: 8551
          protocol: TCP
      env:
        - name: MODEL_PATH
          value: "s3://bucket/model.pkl"
        - name: BUCKET_ENDPOINT
          value: "<your-s3-bucket-endpoint>"
        - name: BUCKET_SECRET_KEY
          value: "<your-s3-secret-key>"
        - name: BUCKET_ACCESS_KEY
          value: "<your-s3-access-key>"
```

## Step 3 - Deploy
Run the following command in order to deploy the resources mentioned in the `generated-container-model/deployment.yml` file:

```
kubectl apply -f containerized_models.yml
```

This command will deploy a `ResourceQuota`, a `Service` and a `Deployment` under the namespace specified in the `generated-container-model/deployment.yml` file (`containermodel` by default).


## Step 4 - Running a remote scan

### Update Scan definition file with valid endpoints
Update `predict_endpoint` field under `models` section in your `scan_definition.yaml` file to the service endpoint. The service endpoint can be created as follows:

`http://<service-name>.<namespace>.svc.cluster.local:8551/predict`

`<service-name>` : should be the same as `metadata.name` under `kind:Service` in `generated-container-model/deployment.yml` file.
`<namespace` : `containermodel` (default namespace)

### SSH into the bastian host 
This step is only need if you don't have access to kubernetes from your local machine. SSH into the bastian host which has access to the k8s cluster.

If you have local access, then install certifai-client from `packages/all` folder inside the toolkit.
`pip install cortex-certifai-client*.zip`

### Trigger the remote scan
`certifai remote scan -f <path-to-scan-definition> -o <output-directory-path> --alias <alias>`
