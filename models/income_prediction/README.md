# Income Prediction example

This example uses the Income Prediction dataset originally sourced from
[Kaggle](https://archive.ics.uci.edu/ml/datasets/census+income).
This is a binary classification example that predicts if a person's income
is less than or greater than $50K.

 The example shows how to use the Certifai Model SDK to wrap trained models into services
 so they can be scanned using the
  [Certifai toolkit](https://cognitivescale.github.io/cortex-certifai/docs/about).

 Specifically, it shows how to use the Certifai toolkit to:
  * wrap a single model as a service, using a customized wrapper
  * scan the model

## Wrap a single model using a customized wrapper  

1. Make sure you have activated your Certifai toolkit environment:
```
conda activate certifai
```

2. Install `xgboost` using conda:
```
conda install -c conda-forge xgboost
```

2. To train the example model:
```
python train.py
```
This generates the trained model as `adult_income_xgb.pkl`.

3. To wrap the model and run it as a service:
```
python app_xgb.py
```

You should see output similar to:
```
* Serving Flask app "certifai.model.sdk.simple_wrapper" (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: off
```

This production gunicorn prediction service requires Certifai version 1.3.6 or later.
It is supported on Linux and Mac, not Windows. To run with the development
server, see [the H2O German Credit example](../h20_dai_german_credit/app_h2o_mojo_pipeline.py)


4. To test the model service, in another terminal activate your Certifai toolkit
environment and run the test script:
```
conda activate certifai
python app_test.py
```
The tests create output similar to:
```
Response from model: [200] {"payload":{"labels":[0,1],"predictions":[0],"scores":[[0.8228642344474792,0.17713576555252075]],"threshold":null}}
```

## Explain model

A scan definition is provided in `income_explain_definition.yaml`. It defines
an explanation scan that generates Shap explanations.

1. To scan the income prediction model:
```
certifai scan -f income_explain_definition.yaml
```
This will create scan reports in the `./reports` folder.

2. To view the reports in the Certifai console:
```
certifai console ./reports
