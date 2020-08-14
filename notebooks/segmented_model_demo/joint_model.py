""" 
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/7998b8a481fccd467463deb1fc46d19622079b0e/LICENSE.md
"""
from typing import List, Tuple

from certifai.common.hosted_model import IHostedModel

import numpy as np


class JointModel:
    def __init__(self, segment_models_idx_mapping: List[Tuple[int, IHostedModel]]):
        self.segment_models_idx_mapping = segment_models_idx_mapping

    def predict(self, X):
        result = np.empty(len(X), dtype='int')
        accounted = 0
        for col_idx, model in self.segment_models_idx_mapping:
            seg_idxs = np.where(X[:, col_idx] > 0.5)[0]
            if len(seg_idxs) > 0:
                accounted += len(seg_idxs)
                result[seg_idxs] = model.predict(X[seg_idxs])
        return result
