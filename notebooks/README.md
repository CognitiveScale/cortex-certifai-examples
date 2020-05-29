# Cortex Certifai Notebooks
This directory contains *Jupyter notebooks* illustrating how to use Certifai in a notebook environment.

### Analyze Feature Usage

In this notebook Certifai will be used to generate counterfactual explanations of two models' predictions for a given
dataset.  By construction these will be data points optimized to be close to the model's decision boundary under
a normalizing constraint of sparsity in changed features over the corresponding original data points.

These counterfactual differences will then be analyzed to obtain a frequency of occurrence of each feature in them,
which is plotted as a histogram for each of two comparative models built on the same dataset.

### Azure ML Model Headers Demo

The Azure Model headers demo example notebook highlights the end-to-end process of running a Certifai fairness evaluation by starting with training, testing, and deploying a sklearn model as a web service with token-based Authentication on Azure, using Azure Containerized Instance(ACI) and launching a Certifai model scan on the deployed model in the same notebook. The example notebook can be run either on local machine or on an Azure-hosted notebook environments.

### Clean Start 

This notebook builds up a scan definition from first principles, against a local model trained within the notebook. That definition will then be used to run scans and save the results. Finally the scan definition will be extracted as YAML, which could be used to run the same scan (potentially on revised models or datasets) via the Certifai stand-alone scanner.

### Clean Start (Soft Output)

The CleanStart notebook with soft outputs required for SHAP explanations.

### Fairness Metrics

In this notebook a scan definition will be created to perform multiple fairness analyses other than the burden-based
default used by the Certifai counterfcatual framework.

Specifically looking at two widely used measures of fairness detailed below.  For the purposes of discussion, things will be defined in terms of the following random variables:

* `X` - the input to the model (i.e. - the features)
* `C` - the class predicted by the model
* `Y` - the actual (ground truth) class
* `G` - the protected group membership.  Note that if the protected grouping feature is included in the data given to the model then for some deterministic `f`, `G = f(X)`.  However, this need not be the case (when it is not the model is said the be trained with 'fairness by unawareness' (which has no theoretical guarantees in regard to actual achieved fairness)

### Hidden Features

This notebook will be exploring fairness by unawareness through several analyses. In the original dataset the model has access to the protected grouping features of 'age' and 'status'. We will explore two variations:

Firstly by building a model that does not have access to the protected features and see to what degree that imporves fairness (this is fairness by unawareness)

Secondly by adding an extra protected feature ('pseudo') which is randomly assigned and thus has no correlation to anything else - this will act as a baseline for how fair we could expect a model to be that truly has no information about a protected feature even through correlated features.

### Scan From Definition

In this notebook a Certifai Scan will be run from an existing scan definition file.

### SHAP

This notebook will run an explainability analysis using SHAP and graph some summary plots of feature importance.

### Documentation
Certifai documentation is available here: https://cognitivescale.github.io/cortex-certifai/docs/about

