# H2O Driverless AI (DAI) Scoring Pipeline Example

**Dataset Used** - This example uses the German Credit dataset originally sourced from [Kaggle](https://www.kaggle.com/uciml/german-credit).

The prepared dataset file used in this example is available in the
[german credit model dataset](../german_credit/german_credit_eval.csv) in this repository, or at `examples/datasets/german_credit_eval.csv` in the
[Certifai Toolkit](https://www.cognitivescale.com/download-certifai/).


# Train and Download the Scoring Pipeline

1. Clone this repository.

2. Upload the dataset in this repository at [models/german_credit/german_credit_eval.csv](../german_credit/german_credit_eval.csv) to
H2O's Driverless AI and use it to auto-learn an ML model.

3. Select 'Click for Actions' and then 'Predict'.

4. Set the target column to 'outcome' and launch the experiment. The experiment
will run for about 30-40 minutes.

5. After completion of the Driverless AI Experiment, download the scoring pipeline that you want to scan with Certifai.

  Download either the [Python Scoring Pipeline](http://docs.h2o.ai/driverless-ai/latest-stable/docs/userguide/scoring-standalone-python.html#running-the-python-scoring-pipeline-alternative-method) or the [Mojo Scoring Pipeline](https://s3.amazonaws.com/artifacts.h2o.ai/releases/ai/h2o/dai/rel-1.8.5-64/docs/userguide/scoring-mojo-scoring-pipeline.html#mojo-scoring-pipeline-files).

  We recommend the MOJO Scoring Pipeline - for this example it is 10-20 times faster.

# Setup the Certifai Scanning Environment

1. Follow the [Toolkit Setup](https://cognitivescale.github.io/cortex-certifai/docs/about) in the Certifai documentation to install the Certifai toolkit into a conda
environment (e.g. `certifai`).

# Scan H2O Mojo Scoring Pipeline
## Setup the Prediction Service

1. In another terminal, setup a different conda environment (e.g. `daimodel`) to run the
prediction service. Due to H2O prerequisites, this must be on Mac or Linux and using python 3.6.
```
conda create -n daimodel python=3.6
conda activate daimodel
```

2. Install the common and model SDK Certifai packages, where `toolkit` is the
path to where you unzipped the Certifai Toolkit. We will use these packages
to run the model as a prediction service that Certifai will use:
```
pip install toolkit/packages/all/*common*.zip
pip install toolkit/packages/all/*model*.zip
```

3. Download and install the MOJO Python runtime from H2O, which is needed to run
the Mojo from python. Follow the [instructions](http://docs.h2o.ai/driverless-ai/latest-stable/docs/userguide/scoring-pipeline-cpp.html#downloading-the-scoring-pipeline-runtimes) to download and install the runtime into your `daimodel` environment.

4. Unzip the MOJO Scoring Pipeline that you downloaded at the end of your
experiment, and copy `mojo.pipeline` into this folder.

5. To run a Driverless AI H2O pipeline, you must have a license. Put your
license key in a file in this folder e.g. `license.txt` and set an
environment variable to it:
```
export DRIVERLESS_AI_LICENSE_FILE="license.txt"
```

5. Review the code in [app_h2o_mojo_pipeline.py](./app_h2o_mojo_pipeline.py).
This code runs the MOJO model in a prediction service that Certifai will use.

6. Start the prediction service:
```
python app_h2o_mojo_pipeline.py
```
You should see output similar to:
```
Loaded 4b16871c-1233-11eb-b801-0242ac110002 from ./pipeline.mojo
 * Serving Flask app "certifai.model.sdk.simple_wrapper" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off

```

7. Test that you can send requests to the prediction service, which is running
on http://127.0.0.1:8551/predict:
```
python app_test.py
```

You should see output similar to:
```
Response from model: [200] {"payload":{"predictions":[1]}}
```

## Scan models using Certifai CLI

1. Follow the instructions in the [Certifai documentation](https://cognitivescale.github.io/cortex-certifai/docs/about) under
'Toolkit > CLI Usage > Define and run scans locally' to define and test a
scan definition for the German Credit example. The only difference from
the example in the documentation is that you need to set the `predict_endpoint`
to http://127.0.0.1:8551/predict
rather than http://127.0.0.1:5111/german_credit_dtree/predict.

  Alternatively, you can use
  the `german_credit_h2o_dai_scan_definition.yaml` provided in this folder to
  perform the trust scan. A
  second definition, `german_credit_h2o_dai_explain_definition.yaml` is provided
  to illustrate a scan that generates counterfactual explanations.

2. Make sure your prediction service is running in the `daimodel` environment.

3. Run the scan in the `certifai` environment:
```
certifai scan -f german_credit_h2o_dai_scan_definition.yaml
```
  The full trust scan typically runs for 30-60 minutes and creates scan reports in
  the `./reports` folder. The explanations scan takes about 10 minutes.
  NOTE: to get an estimate of how long the scan will
  run and to perform some checks, use the `--preflight` option.

4. To view the reports in the Certifai console:
```
certifai console ./reports
```
  Browse to <http://localhost:8000>.
