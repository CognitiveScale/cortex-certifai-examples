""" 
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/7998b8a481fccd467463deb1fc46d19622079b0e/LICENSE.md
"""
from certifai.common.hosted_model import IHostedModel

class SkLearnSoftWrapper(IHostedModel):
    def __init__(self, skl_model):
        self.skl_model = skl_model

    def predict(self, x):
        return self.skl_model.predict(x)

    def soft_predict(self, x):
        return self.skl_model.predict_proba(x)

    @property
    def supports_soft_scores(self):
        return True
