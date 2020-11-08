# Cortex Certifai Models

The *models* folder contains examples of using the Certifai Model SDK to
wrap trained models in a service
that can be scanned using the Certifai scanner CLI. See the *notebooks* folder
for examples of scanning models in a Jupyter notebook using the Certifai API.


## Certifai Documentation

Refer to the
[Cortex Certifai documentation](https://cognitivescale.github.io/cortex-certifai/docs/about)
for detailed information about Cortex Certifai.

## Models Table of Contents

| Model Folder | Description | Task Type | Language | Model Framework |
| --- | --- | --- | --- | -- |
| [containerized_model](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/containerized_model) | Provides a template for containerizing prediction services  |  |  | python, H2O MOJO |
| [german_credit](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/german_credit) | Illustrates using the Certifai Model SDK to run a single (hard or soft-scoring) model in a service or to run multiple models in a service. Also shows scanning a model within a python script using the API.  |  Binary classification | python | sklearn |
| [h2o_dai_german_credit](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/h2o_dai_german_credit) | Illustrates using the Certifai Model SDK to create a gunicorn prediction service from an H2O MOJO, and scan it for trust scores or for explanations.  |  Binary classification | python | H2O MOJO |
| [iris](https://github.com/CognitiveScale/cortex-certifai-examples/tree/master/models/iris) | Illustrates using the Certifai Model SDK to run a single multi-class model in a service, using a customized model wrapper  |  Multi-class classification | python | sklearn |
