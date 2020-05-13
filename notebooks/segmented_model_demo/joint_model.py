from typing import List

import numpy as np


class JointModel:
    def __init__(self, segment_models: list, segment_selection_column_idxs: List[int]):
        self.segment_models = segment_models
        self.segment_selection_column_idxs = segment_selection_column_idxs

    def predict(self, X):
        result = np.empty(len(X), dtype='int')
        accounted = 0
        for idx, model in enumerate(self.segment_models):
            seg_idxs = np.where(X[:, self.segment_selection_column_idxs[idx]] > 0.5)[0]
            accounted += len(seg_idxs)
            result[seg_idxs] = model.predict(X[seg_idxs])
        return result
