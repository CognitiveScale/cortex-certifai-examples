"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""
from certifai.model.sdk import SimpleModelWrapper


# All user-defined code that is to be used in the prediction wrapper must be in
# instance methods in the wrapper class, or in imported modules
# defined in set_global_imports

class XgboostWrapper(SimpleModelWrapper):
    def __init__(self, *args, **kwargs):
        self.metadata = kwargs.pop('metadata', {})
        self.task_type = self.metadata.get('task_type', 'binary-classification')
        SimpleModelWrapper.__init__(self, *args, **kwargs)

    def set_global_imports(self):
        """Override this method to make external global imports
        When using external imports override the method to provide necessary imports.
        Make sure to mark them `global` to
        be used by certifai interpreter correctly.

        :return: None
        """
        global xgb
        import xgboost as xgb
        global np
        import numpy as np

    def soft_predict(self, npinstances):
        """Override this method for custom soft scoring model predictions (binary/multiclass)

        :param npinstances: np.ndarray
        :return: np.ndarray
        """
        results = self.model.predict(xgb.DMatrix(data=npinstances))
        if self.task_type == 'binary-classification':
            # certifai needs scores for both classes to create `score -> outcome label` mappings, whereas
            # XGBoost-DMatrix predict returns a single score for binary-classification
            return np.column_stack((1. - results, results))
        else:
            # multiclass-classification case (XGBoost DMatrix returns scores for all classes)
            return results

    def predict(self, npinstances):
        """Predict override for hard models. In case of XGBoost-DMatrix this is invoked only in case of regression use-case

        :param npinstances: np.ndarray
        :return: np.ndarray
        """
        # regression uses `predict`(hard models) as compared to `soft_predict`(soft scoring models)
        results = self.model.predict(xgb.DMatrix(data=npinstances))
        return results


# These imports are used in launching the prediction service. They are not
# used within the prediction service
import os
import pickle
from utils import fetch_model, load_metadata


def main():
    metadata = load_metadata()
    local_model_path = fetch_model()
    model_pickle = pickle.load(open(local_model_path, 'rb'))
    model = model_pickle.get('model')
    encoder = model_pickle.get('encoder')
    threshold = model_pickle.get('threshold')

    # soft-scoring by design is intended to be used with classification
    # regression is represented as hard-scoring model
    supports_soft_scores = False if metadata.get('task_type') == 'regression' else True
    if supports_soft_scores and not metadata.get('outcomes'):
        raise ValueError('outcome labels not provided for soft-scoring models. check metadata.yml')
    app = XgboostWrapper(model=model,
                         encoder=encoder,
                         host='0.0.0.0',
                         supports_soft_scores=supports_soft_scores,
                         threshold=threshold,
                         score_labels=metadata.get('outcomes', None),
                         metadata=metadata
                         )
    app.set_global_imports()  # needed if not running in production mode
    # Production mode requires Certifai 1.3.6 or higher
    app.run(production=True, log_level='warning', num_workers=3)
    # Replace above with following to run in development mode
    # app.run()


if __name__ == '__main__':
    from pathlib import Path

    os.environ[
        "PYTHONPATH"] = str(Path.joinpath(Path(__file__).parent).resolve())
    main()
