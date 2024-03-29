# Iris classification example

This example uses the [Iris plants dataset](https://scikit-learn.org/stable/auto_examples/datasets/plot_iris_dataset.html)
 provided with sklearn. This is a multi-class classification use case with no
 favorability (outcomes are not favorable or unfavorable).

 The example shows how to use the Certifai Model SDK to wrap trained models into services
 so they can be scanned using the
  [Certifai toolkit](https://cognitivescale.github.io/cortex-certifai/docs/about).

 Specifically, it shows how to use the Certifai toolkit to:
  * wrap a single model as a service, using a customized wrapper
  * scan the model
  * use either an sklearn or xgboost classifier as the model

## Wrap a single model using a customized wrapper  

1. Make sure you have activated your Certifai toolkit environment:
```
conda activate certifai
```

2. Install `xgboost` using conda:
```
conda install -c conda-forge xgboost
```

If you do not want to install `xgboost`, comment out the lines in `train.py`
that train and save the xgboost model.

3. To train the example model:
```
python train.py
```
This generates the trained model as `iris_svm.pkl`.

4. To wrap the model and run it as a service:
```
python app_svm.py
```

The model is surfaced on endpoint `http://127.0.0.1:8551/predict`

The code in `app_svm.py` shows how to use a customized wrapper. In this case,
it maps the model responses from numbers (0, 1, 2) to the names of the
Iris species.

The code in `app_xgb.py` is identical except that it runs the XGBoost classifier.

5. To test the model service, in another terminal activate your Certifai toolkit
environment and run the test script:
```
conda activate certifai
python app_test.py
```
The tests create output similar to:
```
Response from model: [200] {"payload":{"predictions":[0,1,2]}}

Response from shutdown: [200] Shutting down
```
At the end of the tests, the service is shutdown using the `shutdown` endpoint.

## Scan model

A scan definition is provided in `iris_scanner_definition.yaml`. It defines
a scan that evaluates robustness, explainability, performance and explanations.
Fairness does not apply to this use case.

1. To scan the iris model:
```
certifai scan -f iris_scanner_definition.yaml
```
This will create scan reports in the `./reports` folder.

2. To view the reports in the Certifai console:
```
certifai console ./reports
