from sklearn import preprocessing
import pandas as pd
import numpy as np
import pickle
import time

from sklearn import preprocessing
import pandas as pd
import numpy as np
from  utils.german_credit_schema import load_german_dict

german_dict = load_german_dict()

num_col = [1,  4,  7, 10, 15, 17]
cat_col = [0,  2,  3,  5,  6,  8,  9, 11, 12, 13, 14, 16, 18, 19]


# Create transform for categorical data:
class Encoder():
    def __init__(self):
        self.mean__ = 0
        self.scale_ = 1

    def encodeColumn(self, oldCol, labels):
        encoder = preprocessing.OneHotEncoder()
        encoder.fit(np.array(labels).reshape(-1,1))

        to_transform = [[c] for c in oldCol]
        newCol = encoder.transform(to_transform)

        return newCol.toarray()

    def fit(self, X):
        #Compute the mean and std to be used for later scaling.

        self.mean_ = np.zeros(X.shape[1])
        self.scale_ = np.ones(X.shape[1])

        X_numeric = X.iloc[:, num_col]

        scaler = preprocessing.StandardScaler().fit((X_numeric.values).astype(float))

        self.mean_[num_col] = scaler.mean_
        self.scale_[num_col]  = scaler.scale_

        return self

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):
            X  = pd.DataFrame(X)

        feature_names = []

        for idx, header in enumerate(X):
            newdf = pd.DataFrame()

            if idx in cat_col:
                encoded_col = self.encodeColumn(X[header], german_dict[idx])
                encoded_col = encoded_col.reshape((X.shape[0], len(german_dict[idx])))
            if idx in num_col:
                encoded_col = ((X[header].values).astype(float) - self.mean_[idx])/self.scale_[idx]

            # sorted due to OneHotEncoder returning a sorted encoding
            feature_names.append(german_dict[idx])
            newdf = pd.DataFrame(encoded_col, columns=sorted(german_dict[idx]))

            if idx == 0:
                trans_df = newdf
            else:
                trans_df = pd.concat([trans_df, newdf], axis=1, sort=False)

        # retain original ordering of encoding
        feature_names = [item for sublist in feature_names for item in sublist]
        trans_df = trans_df.reindex(columns=feature_names)
        return trans_df

