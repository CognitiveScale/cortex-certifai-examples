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
| CleanStart.ipynb - Building a scan programmatically |  Illustrates the use of Certifai to create and run a fairness scan of a locally defined model from first principles. Again, one of the scan runs produced by this notebook will be saved for viewing |  Binary classification |  SVM <br /> Logistic Regression |  Fairness (by feature) |   |
|  CleanStart(soft-output).ipynb - Building a scan programmatically |  A beta version of the CleanStart notebook for models that produce soft outputs (like probabilities) rather than discrete labels. |  Binary classification | SVM <br /> Logistic Regression | Fairness (by feature) | Soft outputs |
| CleanStartSegmented.ipynb - Building a scan programmatically |  Provides an initial illustration of how to accommodate segmented models in Certifai notebooks. |  Binary classification | SVM <br /> Logistic Regression  | Fairness (by feature) |  Segmented models |
| ScanFromDefinition.ipynb - Running the scanner within a notebook from a definition file  | Illustrates the use of Certifai to generate reports based upon an existing scan definition, with multiple models and multiple analysis types which can be run as a single evaluation.   | Binary classification  | Logistic Regression  |  Fairness (by feature) |   |
|  AnalyzeFeatureUsage.ipynb - Analyzing Feature Usage | Illustrates the use of Certifai to create and run an explanations scan of a locally defined model from first principles. It then analyzes and displays feature distribution of the counterfactuals.  |  Binary classification | Decision Tree <br /> Logistic Regression | Explanations |  Feature Occurrence <br /> Frequency by Model |
| HiddenFeatures.ipynb |  Illustrates the use of Certifai to analyze bias towards protected classes in a model. We show there can still be residual unfairness even if the model is not given access to the protected features. |  Binary classification |  Logistic Regression |  Fairness <br /> Explanations |  Protected features |
| FairnessMetrics.ipynb - Using Different Fairness Metrics | Builds a scan definition to perform multiple fairness analyses other than the burden-based default used by the Certifai counterfactual framework.
Specifically, you examine two widely used measures of fairness: demographic parity and equal opportunity. | Binary Classification | SVM <br /> Logistic Regression | Fairness  | Demographic parity <br /> Equal opportunity <br /> Ground Truth |
| SHAP.ipynb - SHAP explanations | Illustrates the use of an alternative explanation type (Kernel SHAP) to provide both an explainability measure for a model and explanations for individual predictions. SHAP may be used as an alternative to Certifai counterfactual explanation in circumstances where feature weights rather than counterfactual exemplars are preferred. | SVM <br /> Logistic Regression | Explanations  | SHAP Explanations |
|  PracticalIssues.ipynb - Practical Issues |   | Illustrates a couple of practical issues that may occur in typical deployments: <br /> - Pre-encoded data - this notebook shows how to handle datasets in which categorical features have already been encoded as one-hot columns (e.g. - by an ETL process). Explanations are still surfaced with normal categorical values, and the results will be equivalent to those which would have been obtained using an unencoded dataset (with a suitable encoder for the model). <br /> - Bucketing of granular or continuous fairness grouping features | Binary Classification | SVM <br /> Logistic Regression | Fairness (burden) | One-hot encoding <br /> Numerical fairness feature groups |
| xgboostDmatrixExample.ipynb - Running Cortex Certifai fairness evaluation on xgboost model to predict adult income | Illustrates how to accommodate Xgboost models trained with DMatrix data structure in Certifai Notebooks. | Binary Classification | Xboost (XBG) | Fairness | Xboost models <br /> DMatrix data structure
| CertifaiSageMakerExample.ipynb - Running Cortex Certifai Scan on Sklearn model built and deployed on AWS Sagemaker using Certifai Model Connectors | Uses ml.m4.xlarge Sagemaker notebook instance to
create sklearn models to classify german credit loan risk (predict whether loan will be granted or not) and evaluate fairness. |  Binary Classification | SVM <br /> Logistic Regression | Fairness  |  Sagemaker |
| BringInYourOwnModel.ipynb - Building a scan programmatically with your own model | Part one of a tutorial that takes the data scientist through model preparation and scan. This notebook/tutorial is also packaged as part of the toolkit and can be accessed at `examples/notebooks/BringingInYourOwnModel.ipynb`. | Binary Classification | SVM <br /> Logistic Regression | Fairness  <br /> Explainability <br />  Robustness |   |
|  german_credit_azure_ml_demo.ipynb | Takes the data scientists through the end-to-end process of building credit risk (loan approval) models, deploying the models as containerized web services with header-based authentication in an Azure-ML workspace, and running a Certifai scan to analyze model fairness. | Binary Classification  | SVM <br /> Logistic Regression | Fairness (by feature) | Azure Machine Learning Notebook VM  |
| model_train_part1.ipynb |  Illustrates how to start the multiclass classification task type scan. |  Multiclass Classification |  Logistic Regression | Performance Metric: Accuracy  <br /> Explainability-Explanations <br />
Fairness (by feature) | One-hot encoding <br /> Target encoded features |  
| certifai_multiclass_evaluation_part2.ipynb |  Illustrates the second part of the multiclass classification task type. |  Multiclass Classification |  Logistic Regression | Performance Metric: Accuracy  <br /> Explainability-Explanations <br />
Fairness (by feature) | One-hot encoding <br /> Target encoded features |
