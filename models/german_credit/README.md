# German Credit example

This example uses the German Credit dataset originally sourced from
(Kaggle)[https://www.kaggle.com/uciml/german-credit]. This is a binary
classification example.

 The example shows how to use the Certifai Model SDK to wrap trained models into services
 so they can be scanned using the
 (Certifai toolkit)[https://cognitivescale.github.io/cortex-certifai/docs/about].

Specifically, it shows how to use the Certifai toolkit to:
 * wrap a single model as a service
 * implement a composite service that wraps multiple models
 * scan the models

## Wrap a single model as a service
Make sure you have activated your Certifai toolkit environment:
```
conda activate certifai
```

To train the example model:
```
python train.py
```
This generates the trained model as `german_credit_dtree.pkl`.

To wrap the model and run it as a service:
```
python app_dtree.py
```
The model is surfaced on endpoint `http://127.0.0.1:8551/predict`


To test the model service, in another terminal activate your Certifai toolkit
environment and run the test script:
```
conda activate certifai
python app_test.py
```
The tests create output similar to:
```
Response from model: [200] {"payload":{"predictions":[1]}}

Response from shutdown: [200] Shutting down
```
At the end of the tests, the service is shutdown using the `shutdown` endpoint.

## Implement a composite service
Make sure you have activated your Certifai toolkit environment:
```
conda activate certifai
```

To train the example models:
```
python app_dtree.py
```
This generates the trained models as `german_credit_{model}.pkl`.

To wrap the models and run them as a service:
```
python composed_app.py
```
The models are surfaced on endpoints `http://127.0.0.1:8551/{model}/predict`

To test the model service, in another terminal activate your Certifai toolkit
environment and run the test script:
```
conda activate certifai
python composed_app_test.py
```
The tests create output similar to:
```
Response from dtree/predict: [200] {"payload":{"predictions":[1]}}

Response from logit/predict: [200] {"payload":{"predictions":[1]}}

Response from mlp/predict: [200] {"payload":{"predictions":[1]}}

Response from svm/predict: [200] {"payload":{"predictions":[1]}}

Response from health: [200] OK
Response from shutdown: [200] Shutting down
```
At the end of the tests, the service is shutdown using the `shutdown` endpoint.

## Scan models

A scan definition is provided in `german_credit_scanner_definition.yaml`. It defines
a scan that evaluates robustness, fairness, explainability, performance and explanations
for each of the models.

To scan the models, first run the composite service:
To wrap the models and run them as a service:
```
python composed_app.py
```

In another terminal, run Certifai:
```
certifai scan -f german_credit_scanner_definition.yaml
```
This will create scan reports in the `./reports` folder.

To view the reports in the Certifai console:
```
certifai console ./reports
```
