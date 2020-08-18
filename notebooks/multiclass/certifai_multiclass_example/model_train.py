#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
import joblib
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

# In[3]:


# model training preparation
base_path = '../..'
all_data_file = f"{base_path}/datasets/german_credit_eval_multiclass_encoded.csv"

df = pd.read_csv(all_data_file)

cat_columns = [
    'checkingstatus',
    'history',
    'purpose',
    'savings',
    'employ',
    'status',
    'others',
    'property',
    'age',
    'otherplans',
    'housing',
    'job',
    'telephone',
    'foreign'
]

label_column = 'outcome'

# Separate outcome
y = df[label_column]
X = df.drop(label_column, axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# In[3]:


# get_ipython().run_cell_magic('writefile', 'model_encoder.py', '\nfrom sklearn.base import BaseEstimator, TransformerMixin\nfrom sklearn.pipeline import Pipeline\nfrom certifai.common.utils.encoding import CatEncoder\nimport numpy as np\n\nclass TransformerCustom(BaseEstimator, TransformerMixin):\n    def __init__(self, \n                 cat_columns,\n                 normalize=True,\n                 cat_column_value_names=None,\n                 data_encoded=False,\n                 string_equivalence=True,\n                 numeric=None):\n        \n        self.encoder = None\n        self._cat_column_value_names = cat_column_value_names\n        self._normalize = normalize\n        self._data_encoded = data_encoded\n        self._cat_columns = cat_columns\n        self._string_equivalence = string_equivalence\n        self._numeric = numeric\n\n    def fit(self, X, y=None):\n        self.encoder = CatEncoder(self._cat_columns,\n                                  X,self._normalize,\n                                  self._cat_column_value_names,\n                                  self._data_encoded,\n                                  self._string_equivalence,\n                                  self._numeric)\n        \n        return self\n\n    def transform(self, X):\n        if isinstance(X,np.ndarray):\n            return self.encoder(X)\n        return self.encoder(X.values)')


# In[4]:


# from model_encoder import TransformerCustom
parameters = {'C': (0.5, 1.0, 2.0), 'solver': ['lbfgs'], 'max_iter': [1000]}
transformer_pipeline = Pipeline(steps=[('scalar', preprocessing.StandardScaler())])
full_pipeline_m = Pipeline(steps=[('full_pipeline', transformer_pipeline),

                                  ('model', GridSearchCV(LogisticRegression(), parameters, cv=5))])
full_pipeline_m.fit(X_train, y_train)
y_pred = full_pipeline_m.predict(X_test.values)
accuracy = full_pipeline_m.score(X_test, y_test)
print(full_pipeline_m, '\naccuracy', accuracy)

# In[5]:


# model persistence. dump trained model binary along with encoder to disk
# first create a model artifact name. used later for model persistence
model = full_pipeline_m
model_artifact_key = 'german_credit_multiclass'
model_dir = 'models'
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
model_path = f'{model_dir}/{model_artifact_key}.joblib'
joblib.dump(model, model_path)
