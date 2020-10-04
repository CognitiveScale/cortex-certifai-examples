# Patient Readmission example

This example shows how to explain models using Certifai in a notebook. It then
shows how to scan the same models for their trust scores
(fairness, explainability and robustness).

## Certifai Scanning in a Notebook

Follow the steps below to use Certifai to explain the models:
1. Train the models using the [patient-readmission-train.ipynb](patient-readmission-train.ipynb) notebook.
2. Run a scan to explain the models using the [patient-readmission-explain-scan.ipynb](patient-readmission-explain-scan.ipynb) notebook, and view the results in the Certifai Console.
3. Investigate the explanations in the [patient-readmission-explain-results.ipynb](patient-readmission-explain-results.ipynb) notebook.

After completing at least steps 1 and 2 above, follow the steps below to use
Certifai to analyze the trust scores for the models:
4. Run a scan to evaluate the trust scores for the models using the [patient-readmission-trust-scan.ipynb](patient-readmission-trust-scan.ipynb) notebook, and view the results in the Certifai Console.
5. Investigate the trust scores in the [patient-readmission-trust-results.ipynb](patient-readmission-trust-results.ipynb) notebook.
