"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper
import pickle
import numpy as np

# The model returns 0, 1, or 2. The service should return the names of the
# species
species = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
def to_species(i):
    return species[i]

# Customize the SimpleModelWrapper to convert the predictions to the species
class IrisApp(SimpleModelWrapper):
    def predict(self, npinstances):
        results = self.model.predict(npinstances)
        return np.vectorize(to_species)(results)

# Load the trained model and its encoder
with open('iris_svm.pkl', 'rb') as f:
    saved = pickle.load(f)
    model = saved.get('model')
    encoder = saved.get('encoder', None)

# Run the wrapped model as a service
app = IrisApp(model=model, encoder=encoder)
app.run()
