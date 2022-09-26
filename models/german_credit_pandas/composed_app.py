"""
Copyright (c) 2022. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import pickle

from certifai.model.sdk import ComposedModelWrapper, PandasModelWrapper

with open('models/german_credit_dtree.pkl', 'rb') as f:
    saved = pickle.load(f)
    dtree_app = PandasModelWrapper(
        model=saved.get('model'),
        encoder=saved['encoder'].transform,
        pandas_kwargs={'columns': saved['columns']}
    )

with open('models/german_credit_logit.pkl', 'rb') as f:
    saved = pickle.load(f)
    logit_app = PandasModelWrapper(
        model=saved.get('model'),
        encoder=saved['encoder'].transform,
        pandas_kwargs={'columns': saved['columns']}
    )

with open('models/german_credit_mlp.pkl', 'rb') as f:
    saved = pickle.load(f)
    mlp_app = PandasModelWrapper(
        model=saved.get('model'),
        encoder=saved['encoder'].transform,
        pandas_kwargs={'columns': saved['columns']}
    )

with open('models/german_credit_svm.pkl', 'rb') as f:
    saved = pickle.load(f)
    svm_app = PandasModelWrapper(
        model=saved.get('model'),
        encoder=saved['encoder'].transform,
        pandas_kwargs={'columns': saved['columns']}
    )

composed_app = ComposedModelWrapper()
composed_app.add_wrapped_model('/german_credit_dtree', dtree_app)
composed_app.add_wrapped_model('/german_credit_logit', logit_app)
composed_app.add_wrapped_model('/german_credit_svm', svm_app)
composed_app.add_wrapped_model('/german_credit_mlp', mlp_app)
composed_app.run()
