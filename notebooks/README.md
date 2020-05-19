# Cortex Certifai Notebooks
This directory contains *Jupyter notebooks* illustrating how to use Certifai in a notebook environment.

### Azure ML Model Headers Demo

 Azure Model headers demo example notebook highlights end-to-end process of running a Ceritifai Fairness evaluation by starting out with training, testing and deploying a sklearn model as a web service with token based Authentication on Azure, using Azure Containerzed Instance(ACI) and launcing a Certifai model scan on the deployed model in the same notebook. The exame notebook can be run either on local machine or on Azure hosted notebook environments.

### Bringing In Your Own Model to Certifai

 Bringing In Your Own Model to Certifai example demonstrates how create a scan in Certifai using your own model. In this example the model being used is Logistic Regression. We will show how to configure the model to be used in Certifai, and run a scan on it with key evaluation metrics:

 * Fairness
 * Explainability
 * Robustness

The end result will be a scan definition file which contains the meta data from our scan, which can be used for running scans in the CLI and in Part 2 of this tutorial.

### Documentation
These tutorials have docs to be followed along, which can be found at: https://cognitivescale.github.io/cortex-certifai/docs/about

