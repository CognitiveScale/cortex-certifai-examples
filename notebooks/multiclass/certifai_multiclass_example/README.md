# Certifai Target Encoded Multiclass Evaluation Example

The Following example setup demonstrates how to create Certifai model evaluation scan for multi-class classification problem with dataset containing one-hot and target encoded features

## Notebooks

- `model_train_part1` : Part 1 of two part example which trains a scikit-learn logistic classifier model to predict
  loan granted, loan denied or further inspection labels on German Credit multi-class dataset (refer to data_generation notebook in the root directory) and persists the model to disk

- `certifai_multiclass_evaluation_part2.ipynb` : Part 2 of two part example which sets up the Certifai multi-class evaluation scan on the logistic classifier model (trained in part 1 of the example) with evaluation dataset encoded into one-hot and target encoded features
