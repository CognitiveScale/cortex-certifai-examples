"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import pickle

from certifai.model.sdk import ComposedModelWrapper, SimpleModelWrapper

with open('models/german_credit_dtree.pkl', 'rb') as f:
    saved = pickle.load(f)
    dtree_app = SimpleModelWrapper(
        model=saved.get('model'),
        encoder=saved.get('encoder', None)
    )

with open('models/german_credit_logit.pkl', 'rb') as f:
    saved = pickle.load(f)
    logit_app = SimpleModelWrapper(
        model=saved.get('model'),
        encoder=saved.get('encoder', None)
    )

with open('models/german_credit_mlp.pkl', 'rb') as f:
    saved = pickle.load(f)
    mlp_app = SimpleModelWrapper(
        model=saved.get('model'),
        encoder=saved.get('encoder', None)
    )

with open('models/german_credit_svm.pkl', 'rb') as f:
    saved = pickle.load(f)
    svm_app = SimpleModelWrapper(
        model=saved.get('model'),
        encoder=saved.get('encoder', None)
    )

composed_app = ComposedModelWrapper()
composed_app.add_wrapped_model('/german_credit_dtree', dtree_app)
composed_app.add_wrapped_model('/german_credit_logit', logit_app)
composed_app.add_wrapped_model('/german_credit_svm', svm_app)
composed_app.add_wrapped_model('/german_credit_mlp', mlp_app)
#composed_app.run(production=True)
composed_app.run()
