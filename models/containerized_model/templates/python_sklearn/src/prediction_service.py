"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""
from certifai.model.sdk import SimpleModelWrapper

# All user-defined code that is to be used in the prediction wrapper must be in
# instance methods in the wrapper class, or in imported modules
# defined in set_global_imports

class SklearnWrapper(SimpleModelWrapper):
    def __init__(self, *args, **kwargs):
        self.metadata = kwargs.pop('metadata', {})
        self.outcomes = []
        outcomes_from_metadata = self.metadata.get('outcomes')
        if outcomes_from_metadata is not None:
            self.outcomes = outcomes_from_metadata

        self.columns = []
        cols_from_metadata = self.metadata.get('columns')
        if cols_from_metadata is not None:
            self.columns = cols_from_metadata
        SimpleModelWrapper.__init__(self, *args, **kwargs)

    def set_global_imports(self):
        """
        Override this method to make external global imports
        When using external imports override the method to provide necessary imports.
        Make sure to mark them `global` to
        be used by certifai interpreter correctly. set once,use throughout.
        :return: None
        """
        # e.g .
        # global xgb
        # import xgboost as xgb

    def soft_predict(self, npinstances):
        """
        Override this method for custom soft scoring model predictions
        :param npinstances: np.ndarray
        :return: np.ndarray
        """
        # reference model by using `self.model` e.g self.model.predict_proba(npinstances)
        # default implementation for sklearn models below.

        if not self._soft_scoring_validated:
            self._validate_soft_scoring()
        return self.model.predict_proba(npinstances)

    def predict(self, npinstances):
        """
        Calls predict on the python model. Works out of the box with sklearn
        models. Override this method for other model frameworks, or to map
        outputs to desired class labels.
        :param npinstances: np.ndarray
        :return: np.ndarray
        """
        # reference model by using `self.model` e.g self.model.predict(npinstances)
        return self.model.predict(npinstances)

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
    app = SklearnWrapper(model=model,
                  encoder=encoder,
                  host='0.0.0.0',
                  supports_soft_scores=False,
                  threshold=None,
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
