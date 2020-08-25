# Cortex Certifai Examples

This directory contains examples and tutorials illustrating how to use Certifai in a notebook environment and CLI.

## Notebooks

The *notebooks* folder contains JupyterLab notebooks which demonstrate how to use various functions of Certifai in a notebook environment. Instructions for getting started with the notebooks and descriptions of the sample notebooks available in this repo and the Certifai Toolkit can be found [here](https://cognitivescale.github.io/cortex-certifai/docs/toolkit/notebook-usage/jupyter).

## Tutorials

The *tutorials* folder contains walkthroughs which demonstrate basic Certifai functionality. A list of tutorials available in this repo can be found in the [tutorials README](/tutorials/README.md).

## Certifai Documentation

Refer to the Cortex Certifai documentation: https://cognitivescale.github.io/cortex-certifai/docs/about for detailed information about Cortex Certifai.

## Notebooks Table of Contents

| Notebook Name | Description | Task Type | Model Types | Evaluation Types | Key Properties |
| --- | --- | --- | --- | --- | --- |
|  CleanStart.ipynb - Building a scan programmatically |  Illustrates the use of Certifai to create and run a fairness scan of a locally defined model from first principles. Again, one of the scan runs produced by this notebook will be saved for viewing |  Binary classification |  SVM <br /> Logistic Regression |  Fairness (by feature) |   |
|  CleanStart(soft-output).ipynb - Building a scan programmatically |  A beta version of the CleanStart notebook for models that produce soft outputs (like probabilities) rather than discrete labels. |  Binary classification |   |  SVM <br /> Logistic Regression |  Fairness (by feature) | soft outputs |
