# H2O Driverless AI (DAI) Scoring Pipeline Example

**Dataset Used** - This example uses the Auto Insurance example originally sourced from from
[Emcien](https://www.sixtusdakurah.com/resources/The_Application_of_Regularization_in_Modelling_Insurance_Claims.pdf).


The prepared dataset file used in this example is available in the
[notebooks/datasets folder](../../notebooks/datasets/auto_insurance_claims_dataset.csv)


# Train and Download the Scoring Pipeline

1. Clone this repository.

2. Upload the dataset in this repository from [../../notebooks/datasets/auto_insurance_claims_dataset.csv](../../notebooks/datasets/auto_insurance_claims_dataset.csv) to
H2O's Driverless AI and use it to auto-learn an ML model.

3. Select 'Click for Actions' and then 'Predict'.

4. Set the target column to 'Total Claim Amount' and launch the experiment.

5. After completion of the Driverless AI Experiment, download the scoring pipeline that you want to scan with Certifai.

  Download the [Mojo Scoring Pipeline](https://s3.amazonaws.com/artifacts.h2o.ai/releases/ai/h2o/dai/rel-1.8.5-64/docs/userguide/scoring-mojo-scoring-pipeline.html#mojo-scoring-pipeline-files).

# Setup the Certifai Scanning Environment

1. Follow [Toolkit > Setup](https://cognitivescale.github.io/cortex-certifai/docs/about) in the Certifai documentation to install the Certifai toolkit into a conda
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
experiment, and copy `pipeline.mojo` into this folder.

5. To run a Driverless AI H2O pipeline, you must have a license. Put your
license key in a file in this folder e.g. `license.txt` and set an
environment variable to it:
```
export DRIVERLESS_AI_LICENSE_FILE="license.txt"
```

5. Review the code in [app_h2o_mojo_pipeline_gunicorn.py](./app_h2o_mojo_pipeline_gunicorn.py).
This code runs the MOJO model in a prediction service that Certifai will use.

6. Start the prediction service.
```
python app_h2o_mojo_pipeline_gunicorn.py
```
You should see output similar to:
```
[2020-11-08 12:52:17,949] INFO in simple_wrapper: starting server on 0.0.0.0:8551
```

This production gunicorn prediction service requires Certifai version 1.3.6 or later.
It is supported on Linux and Mac, not Windows. To run with the development
server, see [the H2O German Credit example](../h20_dai_german_credit/app_h2o_mojo_pipeline.py)

7. Test that you can send requests to the prediction service, which is running
on http://127.0.0.1:8551/predict:
```
python app_test.py
```

You should see output similar to:
```
Response from model: [200] {"payload":{"predictions":[269.3346252441406]}}
```

## Scan models using Certifai CLI

1. Make sure your prediction service is running in the `daimodel` environment.

2. Run the scan in the `certifai` environment:
```
certifai scan -f auto_insurance_scan_definition.yaml
```
  The full trust scan typically runs for 20-40 minutes and creates scan reports in
  the `./reports` folder.

3. To view the reports in the Certifai console:
```
certifai console ./reports
```
  Browse to <http://localhost:8000>.
