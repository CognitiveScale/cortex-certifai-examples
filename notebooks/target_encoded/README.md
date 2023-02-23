# Certifai Evaluation Multi-Class Example Setup

`dataset_generation` directory contains notebooks to:

- create multi-class dataset
- encode above generated dataset features into one-hot and target encoded features columns

`certifai_multiclass_example` directory contains notebooks to:

 - train and persist model
 - setup Certifai scan
 - deploy model as service using Azure Cloud Instance
 - trigger a remote Certifai scan using the above deployed model

## Environment Setup

Follow the below steps to create a sufficient Python environment

- Create a conda environment with additional prerequisites (keras, tensorflow, category-encoders & matplotlib). The `certifai_azure_model_env.yml` conda environment file is provided for this - run: `conda env create -f certifai_multiclass_example/certifai_azure_model_env.yml`
- Follow the [instructions](https://cognitivescale.github.io/cortex-certifai/docs/toolkit/setup/download-toolkit#obtain-certifai-toolkit) to download and install the Certifai toolkit in the current environment


## Dataset Generation (optional)

Target and one-hot encoded versions of the german-credit dataset as a multiclass classfication problem are provided with the example but in-case someone wants to re-generate the data, follow the steps outlined below:

- Generate `german-credit multi-class` dataset using the [dataset generation notebook](./dataset_generation/german_credit_multiclass_dataset_generation.ipynb)
- Encode (target & one-hot) the generated dataset (from above) using the [dataset encoding notebook](./dataset_generation/german_credit_multiclass_dataset_encoding.ipynb)


## Certifai Scanning

Follow the steps below to trigger Certifai scan in the notebook

- Train the model using the [training notebook](./certifai_multiclass_example/model_train_part1.ipynb)
- Initiate Certifai scan using the [evaluation notebook](./certifai_multiclass_example/certifai_multiclass_evaluation_part2.ipynb)


## Deployment and Remote Scanning using Certifai Pro

Follow the steps below to deploy the model to Azure and scan it using Certifai Pro

- Deploy the model (as a service) in Azure using the [model deployment notebook](./certifai_multiclass_example/deploying_model_part3.ipynb)
- Install Certifai Pro in Azure and trigger remote scan using the [remote scanning notebook](./certifai_multiclass_example/remote_scan_part4.ipynb)
