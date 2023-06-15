"""
Copyright (c) 2022. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import pickle

from certifai.model.sdk import PandasModelWrapper

with open('models/german_credit_mlp.pkl', 'rb') as f:
    saved = pickle.load(f)
    model = saved.get('model')
    encoder = saved.get('encoder', None)
    columns = saved.get('columns')

# To enable models with soft-scores use `supports_soft_scores=True` when initializing PandasModelWrapper
# scikit mlp classifier provides default implementation for soft_scores using `predict_proba` method
# in-order to provide own soft scoring method override PandasModelWrapper.soft_predict
# optionally, add ordered list of score_labels. default labels are derived using `model._classes` provided by scikit mlp
# these are ordered wrt to model predict scores. e.g. if score_labels = [1,2] then scores of [0.3,0.7] -> [1,2] labels
# follow certifai.model.sdk docs for more info.
# https://cognitivescale.github.io/cortex-certifai/docs/reference/api

app = PandasModelWrapper(supports_soft_scores=True, model=model, encoder=encoder.transform, score_labels=[1, 2],
                         endpoint_url='/german_credit_mlp/predict', pandas_kwargs={'columns': columns})

# to start production ready gunicorn server use `production=True`
#app.run(production=True)
app.run()
