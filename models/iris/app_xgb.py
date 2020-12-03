"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper
import pickle
import numpy as np
import xgboost as xgb

# The model returns 0, 1, or 2. The service should return the names of the
# species. The score labels must be given in the order of the probabilities
# returned by the model.
species = np.array(['Iris-setosa', 'Iris-versicolor', 'Iris-virginica'])

# Customize the SimpleModelWrapper to convert the predictions to the species
class IrisApp(SimpleModelWrapper):
    def predict(self, npinstances):
        # This method is only used if supports_soft_scores is False
        results = self.model.predict(npinstances)
        return species[results]

# Load the trained model and its encoder
with open('iris_xgb.pkl', 'rb') as f:
    saved = pickle.load(f)
    model = saved.get('model')
    encoder = saved.get('encoder', None)

# Run the wrapped model as a service
app = IrisApp(model=model,
    encoder=encoder,
    supports_soft_scores=True,
    score_labels=species.tolist()
)
app.run()
