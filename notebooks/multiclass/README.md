# Certifai Evaluation Multi-Class Example Setup

`dataset_generation` directory contains notebooks to:

- create multi-class dataset
- encode above generated dataset features into one-hot and target encoded features columns

`certifai_multiclass_example` directory contains notebooks to:

 - train and persist model
 - setup Certifai scan
 - deploy model as service using Azure Cloud Instance
 - trigger a remote Certifai scan using the above deployed model


## Dataset Generation (optional)

Target and one-hot encoded german-credit multi-class dataset is provided with the example but in-case someone wants to re-generate the data, follow the steps outlined below:

- Follow the [instructions](https://cognitivescale.github.io/cortex-certifai/docs/toolkit/setup/download-toolkit#obtain-certifai-toolkit) to download and install the Certifai toolkit
- Install additional prerequisites (keras, tensorflow, category-encoders & matplotlib) using `pip install keras tensorflow category_encoders matplotlib`
- Generate `german-credit multi-class` dataset using the [notebook](https://github.com/CognitiveScale/cortex-certifai-examples/blob/04cd4bcc855825187abd922cf5f349b789517930/notebooks/multiclass/dataset_generation/german_credit_multiclass_dataset_generation.ipynb)
- Encode (target & one-hot) the generated dataset (from above) using the [notebook](https://github.com/CognitiveScale/cortex-certifai-examples/blob/04cd4bcc855825187abd922cf5f349b789517930/notebooks/multiclass/dataset_generation/german_credit_multiclass_dataset_encoding.ipynb)


## Certifai Scanning

Follow the steps below to trigger Certifai scan in the notebook

- Train the model using the [notebook](https://github.com/CognitiveScale/cortex-certifai-examples/blob/04cd4bcc855825187abd922cf5f349b789517930/notebooks/multiclass/certifai_multiclass_example/model_train_part1.ipynb)
- Initiate Certifai scan using the [notebook](https://github.com/CognitiveScale/cortex-certifai-examples/blob/04cd4bcc855825187abd922cf5f349b789517930/notebooks/multiclass/certifai_multiclass_example/deploying_model_part3.ipynb)


## Deployment and Remote Scanning using Certifai Pro

Follow the steps below to deploy the model to Azure and scan it using Certifai Pro

- Deploy the model (as a service) in Azure using the [notebook](https://github.com/CognitiveScale/cortex-certifai-examples/blob/04cd4bcc855825187abd922cf5f349b789517930/notebooks/multiclass/certifai_multiclass_example/deploying_model_part3.ipynb)
- Install Certifai Pro in Azure and trigger remote scan using the [notebook](https://github.com/CognitiveScale/cortex-certifai-examples/blob/04cd4bcc855825187abd922cf5f349b789517930/notebooks/multiclass/certifai_multiclass_example/remote_scan_part4.ipynb)

