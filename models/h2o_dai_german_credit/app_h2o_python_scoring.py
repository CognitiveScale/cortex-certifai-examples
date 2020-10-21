"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper
import pandas as pd
import numpy as np
from numpy import nan
import datatable as dt
from scipy.special._ufuncs import expit
# TODO dynamically determine module to import
from scoring_h2oai_experiment_4b16871c_1233_11eb_b801_0242ac110002 import Scorer

scorer = Scorer()
columns = ['checkingstatus',
    'duration',
    'history',
    'purpose',
    'amount',
    'savings',
    'employ',
    'installment',
    'status',
    'others',
    'residence',
    'property',
    'age',
    'otherplans',
    'housing',
    'cards',
    'job',
    'liable',
    'telephone',
    'foreign'
]
scorer = Scorer()

def _get_prediction_class(preds):
    if preds[0] > preds[1]:
        return 1
    return 2

class GermanCredit(SimpleModelWrapper):
    def predict(self, npinstances):
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=columns)
        predictions = scorer.score_batch(input_dt, output_margin=False).apply(_get_prediction_class, axis=1)
        return predictions.values

if __name__ == "__main__":
    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = GermanCredit(host="0.0.0.0")
    app.run(log_level="warn")
