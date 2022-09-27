# German Credit Example

This example uses the German Credit dataset originally sourced from [Kaggle](https://www.kaggle.com/uciml/german-credit)
. This is a binary classification example.

The example shows how to use the Certifai Model SDK to wrap trained models into services, so they can be scanned using
the [Certifai toolkit](https://cognitivescale.github.io/cortex-certifai/docs/about).

Specifically, it shows how to use the Certifai toolkit to:

* Wrap a single model as a service.
* Implement a composite service that wraps multiple models.
* Scan the models using the Certifai CLI.
* Scan a model using the Certifai Python API.

## Wrap a single model as a service

1. Make sure you have activated your Certifai toolkit environment:

```
conda activate certifai
```

2. To train the example model:

```
python train.py
```

This generates the trained model as `models/german_credit_dtree.pkl`.

3. To wrap the model and run it as a service:

```
python app_dtree.py
```

The model is surfaced on endpoint `http://127.0.0.1:8551/predict`

4. To test the model service, in another terminal activate your Certifai toolkit environment and run the test script:

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

1. Make sure you have activated your Certifai toolkit environment:

```
conda activate certifai
```

2. To train the example models:

```
python train.py
```

This generates the trained models as `models/german_credit_{model}.pkl`.

3. To wrap the models and run them as a service:

```
python composed_app.py
```

The models are surfaced on endpoints `http://127.0.0.1:8551/{model}/predict`

4. To test the model service, in another terminal activate your Certifai toolkit environment and run the test script:

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

## Scan models using CLI

A scan definition is provided in `german_credit_scanner_definition.yaml`. It defines a scan that evaluates robustness,
fairness, explainability, performance, and explanations for each of the models.

1. To scan the models, first run the composite service:

```
python composed_app.py
```

2. In another terminal, run Certifai:

```
certifai scan -f german_credit_scanner_definition.yaml
```

This creates scan reports in the `./reports` folder.

3. To view the reports in the Certifai console:

```
certifai console ./reports
```

## Scan models using API

You can also scan models from python using the Certifai API. The
`explain.py` script illustrates doing this in order to explain a set of predictions.

1. To explain the predictions:

```
python explain.py
```

This creates a scan report in the `./reports` folder containing explanations for the decision tree model.

2. To view the reports in the Certifai console:

```
certifai console ./reports
```

## Wrap a soft-scoring model as a service

1. Soft Scoring MLP classifier model is trained as a part
   of [Wrap a single model as a service](#wrap-a-single-model-as-a-service).

2. To wrap the model and run it as a service:
    ```
    python app_mlp_soft_scoring.py
    ```
   The model is surfaced on endpoint `http://127.0.0.1:8551/german_credit_mlp/predict`.

3. To test the model service, in another terminal activate your Certifai toolkit environment and run the test script:

    ```
    conda activate certifai
    python app_mlp_soft_scoring_test.py
    ```
   The tests create output similar to:
    ```
    Response from model: [200] {"payload":{"labels":[1,2],"predictions":[1],"scores":[[0.9970156761270139,0.0029843238729861045]],"threshold":null}}

    Response from shutdown: [200] Shutting down
    ```
   At the end of the tests, the service is shutdown using the `shutdown` endpoint.

## Scan soft scoring models using CLI

A scan definition for soft scoring model is provided in `german_credit_shap_explanation_scanner_definition.yaml`. It
defines a scan that evaluates SHAP and Counterfactual Explanations for a soft model on a subsample 100 row of
the [German Credit dataset](#german-credit-example).

1. To scan the model, first run the soft scoring model service:
    ```
    python app_mlp_soft_scoring.py
    ```

2. In another terminal, run Certifai:
    ```
    certifai scan -f german_credit_shap_explanation_scanner_definition.yaml
    ```
   This will create scan reports in the `./reports` folder.

3. To view the reports in the Certifai console:
    ```
    certifai console ./reports
    ```
