"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""
from certifai.model.sdk import SimpleModelWrapper
import pickle
import numpy as np
import xgboost as xgb # This import is used in the development server

class Wrapper(SimpleModelWrapper):
    def set_global_imports(self):
        """
        Overridden method to make external global imports in the gunicorn
        production server.
        When using external imports override the method to provide necessary imports.
        Make sure to mark them `global` to be used by certifai interpreter correctly.
        """
        global xgb
        import xgboost as xgb
        global np
        import numpy as np

    def soft_predict(self, npinstances):
        # reference model by using `self.model`
        results = self.model.predict(xgb.DMatrix(data=npinstances))
        return np.array([[1. - x, x] for x in results])


with open('adult_income_xgb.pkl', 'rb') as f:
    saved = pickle.load(f)
    model = saved.get('model')
    encoder = saved.get('encoder', None)

if __name__ == "__main__":
    # since xgboost is a soft-scoring model with single score for each prediction,
    # we override `soft_predict` and provide `threshold` and `score_labels` to
    # get thresholded predictions

    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = Wrapper(host="0.0.0.0",
                  supports_soft_scores=True,
                  model=model,
                  encoder=encoder,
                  score_labels=[0, 1])
    app.run()
    # Replace the previous line with the following to run the production server
    # This requires Certifai version 1.3.6 or later.
    app.run(log_level="warning", production=True, num_workers=3)
