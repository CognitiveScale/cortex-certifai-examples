"""
Copyright (c) 2022. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import pickle

from certifai.model.sdk import PandasModelWrapper

with open('models/german_credit_dtree.pkl', 'rb') as f:
    saved = pickle.load(f)
    model = saved.get('model')
    encoder = saved.get('encoder', None)
    columns = saved.get('columns')

app = PandasModelWrapper(pandas_kwargs={'columns': columns}, model=model, encoder=encoder.transform)
app.run()
