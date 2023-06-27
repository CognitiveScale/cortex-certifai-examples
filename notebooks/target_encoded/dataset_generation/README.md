# Dataset Generation


## Notebooks

- `german_credit_multiclass_dataset_generation`: Creates a neural network model with soft-scoring to transform binary outcome-labels (loan granted/loan denied (1/2) ) [German-Credit-Dataset](https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data) into multiclass problem with three outcome-labels (loan granted/loan denied/further inspection (1/2/3) ) and saves the dataset as csv

- `german_credit_multiclass_dataset_encoding`: Encodes the above generated dataset into target encoded and one-hot encoded feature columns and dumps the generated mappings to disk as json

