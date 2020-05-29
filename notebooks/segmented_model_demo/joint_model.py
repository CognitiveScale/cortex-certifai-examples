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
