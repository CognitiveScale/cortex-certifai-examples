"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import os
import pickle

from certifai.model.sdk import SimpleModelWrapper
from certifai.common.file.locaters import make_generic_locater
from certifai.common.file.interface import FilePath

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def fetch_model_binary(model_path: str) -> bytes:
    """
    Fetches model binary from model_path
    :param model_path: Model path e.g s3://model/dtree.pkl
    :return: Model Binary as bytes
    """
    with make_generic_locater(FilePath(model_path)).reader() as f:
        return f.read()


def read_and_save_file(model_path, default_model_path):
    # Fetch model binary
    model_binary = fetch_model_binary(model_path)
    with open(default_model_path, 'wb') as f:
        f.write(model_binary)


def main():
    model_path = os.getenv('MODEL_PATH')
    if model_path is not None:
        # Copy files from remote path to local
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model', os.path.basename(model_path)))
        read_and_save_file(model_path, default_model_path)
    else:
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model/model.pkl'))
    model_pickle = pickle.load(open(default_model_path, 'rb'))
    model = model_pickle.get('model')
    encoder = model_pickle.get('encoder')
    app = SimpleModelWrapper(model=model, encoder=encoder, host='0.0.0.0')
    app.run(production=True)


if __name__ == '__main__':
    main()
