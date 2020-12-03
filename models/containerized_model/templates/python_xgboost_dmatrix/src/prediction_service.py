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
        self.outcomes = []
        outcomes_from_metadata = self.metadata.get('outcomes')
        if outcomes_from_metadata is not None:
            self.outcomes = outcomes_from_metadata
        self.task_type = self.metadata.get('task_type', 'regression')
        SimpleModelWrapper.__init__(self, *args, **kwargs)

    def set_global_imports(self):
        """
        Override this method to make external global imports
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
        """
        Override this method for custom soft scoring model predictions
        :param npinstances: np.ndarray
        :return: np.ndarray
        """
        results = self.model.predict(xgb.DMatrix(data=npinstances))
        if self.task_type == 'binary-classification':
            return np.array([[1. - x, x] for x in results])
        # elif self.task_type == 'multiclass-classification':
        else:
            return results

    def predict(self, npinstances):
        """
        Converts XGBoost output to regression or classification labels.
        :param npinstances: np.ndarray
        :return: np.ndarray
        """
        results = self.soft_predict(npinstances)
        get_preds = lambda preds: self.get_prediction(preds, self.outcomes)
        return np.apply_along_axis(get_preds, 1, results)

    def get_prediction(self, preds, outcomes=None):
        """
        Given an array of soft output and the list of expected class labels,
        get_prediction returns the appropriate class label based on the class
        probabilities.

        For a regression model, get_prediction returns the single probability.
        """
        if len(preds) == 1:
            return preds[0] # regression
        if len(preds) > 1:
            if outcomes is None or len(outcomes) == 0:
                raise Exception('No outcome labels provided for classification model')
            index = preds.argmax() # position of largest value
            return outcomes[index]

        raise Exception('No prediction returned by model')

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
    app = XgboostWrapper(model=model,
                  encoder=encoder,
                  host='0.0.0.0',
                  supports_soft_scores=metadata.get('supports_soft_scoring', True),
                  threshold=threshold,
                  score_labels=metadata.get('outcomes'),
                  metadata=metadata
                  )
    app.set_global_imports() # needed if not running in production mode
    # Production mode requires Certifai 1.3.6 or higher
    app.run(production=True, log_level='warning', num_workers=3)
    # Replace above with following to run in development mode
    # app.run()

if __name__ == '__main__':
    main()
