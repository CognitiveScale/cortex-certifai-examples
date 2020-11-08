"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""
import pickle
import random
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from certifai.common.utils.encoding import CatEncoder
import xgboost as xgb
import warnings

# supress all warnings
warnings.filterwarnings('ignore')


def main():
    random.seed(0)
    np.random.seed(0)
    # load data into dataframe
    df = pd.read_csv('../../notebooks/datasets/adult_income_eval.csv')

    # Separate outcome
    label_column = 'income'

    y = df[label_column]
    X = df.drop(label_column, axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    cat_columns = [
        'workclass',
        'education',
        'marital-status',
        'occupation',
        'relationship',
        'race',
        'gender',
        'native-country'
    ]
    encoder = CatEncoder(cat_columns, X_train)

    # define hyperparams for training xgboost model
    params = {"objective": "reg:squarederror", 'colsample_bytree': 0.3, 'learning_rate': 0.1,
              'max_depth': 5, 'alpha': 10}

    # encode training data to be used to for model training
    data_dmatrix = xgb.DMatrix(data=encoder(X_train.values), label=y_train)
    # train the xgboost model
    xg_reg = xgb.train(params=params, dtrain=data_dmatrix, num_boost_round=10)

    # calculate accuracy on test-set. using 0.46 as threshold for scoring
    threshold = 0.46
    dtest = xgb.DMatrix(encoder(X_test.values))
    preds = xg_reg.predict(dtest)
    best_preds = map(lambda x: int(x > threshold), preds)
    acc = accuracy_score(y_test, list(best_preds))
    print(f'model accuracy on test set: {acc}')

    # dump model and encoder to disk
    filename = 'adult_income_xgb.pkl'
    model_obj = {
        'model': xg_reg,
        'encoder': encoder
    }

    with open(filename, 'wb') as file:
        pickle.dump(model_obj, file)


if __name__ == "__main__":
    main()
