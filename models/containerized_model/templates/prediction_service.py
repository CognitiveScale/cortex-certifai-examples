"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import os
import io
import pickle

from certifai.model.sdk import SimpleModelWrapper
from certifai.common.file.locaters import make_generic_locater
from certifai.common.file.interface import FilePath


def fetch_model_binary(model_path: str) -> io.BytesIO:
    """
    Fetches model binary from model_path
    :param model_path: Model path e.g s3://model/dtree.pkl
    :return: File-like object with Model Binary as contents
    """
    with make_generic_locater(FilePath(model_path)).reader() as f:
        return io.BytesIO(f.read())


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
