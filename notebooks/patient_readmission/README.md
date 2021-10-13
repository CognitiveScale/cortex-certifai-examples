# Patient Readmission example

This example uses a kaggle dataset [Diabetes 130 US hospitals for years 1999-2008](https://www.kaggle.com/brandao/diabetes) where the task is to predict whether a patient will be readmitted to hospital after being discharged.

This example first shows how to explain models using Certifai in a notebook.
It then shows how to scan the same models for their trust scores
(fairness, explainability and robustness). Lastly, this example shows an alternative
method for explaining a model using Certifai, that can be run with only historic model predictions.

## Certifai Scanning in a Notebook

Follow the steps below to use Certifai to explain the models:

1. Train the models using the [patient-readmission-train.ipynb](patient-readmission-train.ipynb) notebook.
2. Run a scan to explain the models using the [patient-readmission-explain-scan.ipynb](patient-readmission-explain-scan.ipynb) notebook, and view the results in the Certifai Console.
3. Investigate the explanations in the [patient-readmission-explain-results.ipynb](patient-readmission-explain-results.ipynb) notebook.

After completing at least steps 1 and 2 above, follow the steps below to use
Certifai to analyze the trust scores for the models:

4. Run a scan to evaluate the trust scores for the models using the [patient-readmission-trust-scan.ipynb](patient-readmission-trust-scan.ipynb) notebook, and view the results in the Certifai Console.
5. Investigate the trust scores in the [patient-readmission-trust-results.ipynb](patient-readmission-trust-results.ipynb) notebook.

After at lest completing steps 1 and 2 above, follow the steps below to use
Certifai to explain a model via counterfactual sampling.

6. Run two scans to explain a single model via counterfactual sampling using the [patient-readmission-sampling-scan.ipynb](patient-readmission-sampling-scan.ipynb) notebook. The first scan will have direct access to the model, whereas the second will only have the historical predictions from the model. The results can then be viewed in the Certifai Console.
7. Investigate the explanations in the [patient-readmission-sampling-results.ipynb](patient-readmission-sampling-results.ipynb) notebook and compare the results between the two scans.