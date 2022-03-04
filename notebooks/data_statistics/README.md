# Data Statistics and Drift Monitoring 

This folder contains an example for the data statistics evaluation type in Certifai (introduced in v1.13.14). This evaluation type analyzes an evaluation/monitored dataset and compares it to a reference dataset. The following metrics are calculated and analyzed:

1. Data Quality - Counts of missing data (data not present in the monitored data) or counts of unexpected data (data not present in the reference data),
2. Feature Quality - Quartiles for numeric features or distribution counts for categorical features,
3. Feature Drift - Univariate hypothesis testing to detect drift in individual features of the monitored data,
4. Prediction Distribution - Prediction value quartiles for regression tasks or label distribution counts for classification tasks, and
5. Prediction Drift - Univariate hypothesis testing to detect drift in the prediction label.

The example notebooks perform data statistics and drift monitoring on the [UCI Adult Income dataset](https://archive.ics.uci.edu/ml/datasets/Adult).

Package Requirements:
* Certifai
* Matplotlib

----
## Breakdown of artifacts:
* prep_adult_data_drift.ipynb - notebook demonstrating how to prepare and generate data with drift
* adult_drift_data_statistics.ipynb - notebook demonstrating how to use the data statistics in CERTIFAI, processing of reports, and plotting of results
* utils/data_stats_report_utils.py - helper functions for parsing and analysis of the data statistics scan reports
* data/ - contains reference and monitored datasets
* reports/ - contains the scan reports

----
## Instructions for running:

Follow the steps below to use Certifai to run the data statistics evaluation:

1. Generate the reference and monitored datasets using the `prep_adult_data_drift.ipynb` notebook
2. Run the data statistics analysis with the `adult_drift_data_statistics.ipynb` notebook (this is an example of running data statistics via the API)
