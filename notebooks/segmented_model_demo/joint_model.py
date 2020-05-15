from typing import Dict

import numpy as np


class JointModel:
    def __init__(self, segment_models_idx_mapping: Dict[str,Dict]):
        self.segment_models_idx_mapping = segment_models_idx_mapping

    def predict(self, X):
        result = np.empty(len(X), dtype='int')
        accounted = 0
        for _, idx_model_mapping in self.segment_models_idx_mapping.items():
            seg_idxs = np.where(X[:, idx_model_mapping['idx']] > 0.5)[0]
            accounted += len(seg_idxs)
            result[seg_idxs] = idx_model_mapping['model'].predict(X[seg_idxs])
        return result
