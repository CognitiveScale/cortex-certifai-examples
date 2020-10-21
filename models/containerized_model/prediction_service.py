"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import os
import pickle

from certifai.model.sdk import SimpleModelWrapper
from certifai.model.utils.http_util import fetch_model_binary


def read_model():
    model_path = os.getenv('MODEL_PATH')

    # Fetch model binary (returns a file-like object)
    model = fetch_model_binary(model_path)

    # Load and return the pickled model
    return pickle.load(model)


def main():
    model_pickle = read_model()
    model = model_pickle.get('model')
    encoder = model_pickle.get('encoder')
    app = SimpleModelWrapper(model=model, encoder=encoder, host='0.0.0.0')
    app.run(production=True)


if __name__ == '__main__':
    main()
