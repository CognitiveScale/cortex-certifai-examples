# Patient re-admission fast-explain example

This example uses a kaggle dataset [Diabetes 130 US hospitals for years 1999-2008](https://www.kaggle.com/brandao/diabetes) where the task is to predict whether a patient will be readmitted to hospital after being discharged. Please refer to kaggle for more details.

 The example shows how to use the Certifai Model SDK to wrap a trained model into a service and how to generate explanations for its predictions
 using the
 [Certifai toolkit](https://cognitivescale.github.io/cortex-certifai/docs/about).

Specifically, it shows how to use the Certifai toolkit to:
 * wrap a single model as a service
 * generate explanations for the model's predictions using the CLI
 * set up fast-explanation, for generating large numbers of explanations at scale

## Wrap a single model as a service

1. Make sure you have activated your Certifai toolkit environment:
```
conda activate certifai
```

2. To train the example model:
```
python train.py
```
This generates the trained model as `model_mlp.pkl`.  It also generates the datasets that will be used
by the example analysis after some light preprocessing to convert diagnostic codes
to something more sensible.  Optionally `train.py` takes a single integer parameter
that specifies the size of the explanation set to generate.  This defaults to
1000, which is smaller than would justify the use of fast explanations, but is used
by the example since we want to do regular explanations as well here to show both
methods.

3. To wrap the model and run it as a service:
```
python app.py
```
The model is surfaced on endpoint `http://127.0.0.1:8551/predict`


4. To test the model service and Certifai installation, in another terminal activate your Certifai toolkit environment and run the command:
```
conda activate certifai
certifai definition-test -f explain_def.yml
```
The tests create output similar to:
```
Prediction test successful for 'mlp' model against 'evaluation' dataset
Prediction test successful for 'mlp' model against 'explanation' dataset
```

## Generate explanations using the CLI (baseline)

A scan definition is provided in `explain_def.yml`. It defines
a scan that generates explanations for the model.

1. To scan the model, first run the model service (if not already running):
```
python app.py
```

2. In another terminal, run Certifai:
```
certifai explain -f explain_def.yml
```
This will create scan reports in the `./reports` folder.  An explanation dataframe
will also be saved in the usecase folder under `reports` containing a Pandas DataFrame
saved as CSV with both originals and generated counterfactuals.

*Note*: This is the baseline case using the full genetic algorithm approach for all
explanations.  It is provided just for comparative purposes, and this step may be omitted if desired

## Perform one-time precalculation needed to support fast explanations

We will now run the scan in `precalculate` mode.  This derives an exemplar clustering
of the training set (which should be a large sample - in this example it is over 100K rows).
It then calculates full counterfactuals for the exemplars and saves both the clustering
and counterfactual information along with some other metadata in a cache directory
associated with the use-case (in the reports folder).  This saved data is not human-readable
and is intended solely to be used by the fast-explanations step of a subsequent Certifai invokation.

*Note*: This step is computationally expensive, and may take several hours to
complete.  However, it need be performed only once for a given use-case and model, after
which it serves to support arbitrary numbers of generated explanations (see next step)

```
certifai explain -f explain_def.yml --precalculate
```

## Perform a fast explanation

```
certifai explain -f explain_def.yml --fast
```

This will create a report and CSV containing the explanations, exactly as the regular
explain did.

*Note*: This example uses the same definition file as we used for the regular explanations, so
only tries to explain the (relatively small) 1000 row explanation dataset used there.
As a result fixed overheads will mean the overall time ratio to that of the normal
explanation step is not fully representative of the achieved speedup. Feel free to
generate a larger explanation dataset to explore scaling behavior, by running `train.py` with
a numeric parameter to specify a larger explanation set (e.g. - `python train.py 10000`).
If you want to generate multiple different explanation sets for testing, you can rename the generated
one (`diabetic_data_diagnostic_mapped_explain.csv`) and replace the explanation dataset filename in the definition
by editing the `url` field for the explanation dataset in this section of the `explain_def.yml` file:
```
datasets:
- dataset_id: evaluation
  url: diabetic_data_diagnostic_mapped.csv
  has_header: true
  file_type: csv
  delimiter: ','
  quote_character: '"'
- dataset_id: explanation
  url: diabetic_data_diagnostic_mapped_explain.csv
  has_header: true
  file_type: csv
  delimiter: ','
  quote_character: '"'
```
