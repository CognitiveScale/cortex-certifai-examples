# copy of cat_encoder.ipynb ; required for Azure Notebooks

from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
import numpy as np

class CatEncoder:
    def __init__(self, cat_columns, data, normalize: bool=True):
        self.cat_indexes = [data.columns.get_loc(name) for name in cat_columns]
        self.num_indexes = [idx for idx in range(len(data.columns)) if idx not in self.cat_indexes]
        self.encoder = preprocessing.OneHotEncoder()
        self.encoder.fit(data[cat_columns])
        self.num_columns = list(data.columns[self.num_indexes])
        self.cat_columns = cat_columns
        cat_transformed_names = self.encoder.get_feature_names(input_features=self.cat_columns)
        self._transformed_column_names =  self.num_columns + list(cat_transformed_names)
        if normalize:
            self.normalizer = StandardScaler()
            self.normalizer.fit(data.iloc[:, self.num_indexes])
        else:
            self.normalizer = None
    
    def __call__(self, x):
        numeric = x[:, self.num_indexes]
        if self.normalizer is not None:
            numeric = self.normalizer.transform(numeric)
        categorical = self.encoder.transform(x[:, self.cat_indexes]).toarray()
        return np.concatenate((numeric, categorical), axis=1)

    @property
    def transformed_features(self):
        return self._transformed_column_names
