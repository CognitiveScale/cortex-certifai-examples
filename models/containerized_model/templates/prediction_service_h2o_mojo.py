"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper
from certifai.common.file.locaters import make_generic_locater
from certifai.common.file.interface import FilePath

import os
import daimojo.model
import datatable as dt

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

MODEL = None

# <Add columns here>
COLUMNS = []

if len(COLUMNS) == 0:
    print('Columns can not be empty. Please update colums in prediction_service.py file.')
    exit(1)


def fetch_model_binary(model_path: str) -> bytes:
    """
    Fetches model binary from model_path
    :param model_path: Model path e.g s3://model/dtree.pkl
    :return: Model Binary as bytes
    """
    with make_generic_locater(FilePath(model_path)).reader() as f:
        return f.read()


def read_and_save_file(source_path, destination_path):
    # Fetch model binary
    model_binary = fetch_model_binary(source_path)
    with open(destination_path, 'wb') as f:
        f.write(model_binary)

# <Fill in this function and remove the 'raise'>
def _get_prediction_class(preds):
    """
    For a classification model, _get_prediction_class should return the
    appropriate class label based on the class probability.

    For example, for a binary classification model:
        if preds[0] > preds[1]:
            return 1
        return 0
    """
    raise Exception('_get_prediction_class not implemented')



class MojoModelWrapper(SimpleModelWrapper):

    def predict(self, npinstances):
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=COLUMNS)
        predictions = MODEL.predict(input_dt).to_pandas().apply(_get_prediction_class, axis=1)
        return predictions.values


if __name__ == "__main__":
    model_path = os.getenv('MODEL_PATH')
    license_path = os.getenv('H2O_LICENSE_PATH')
    if model_path is not None:
        # Copy files from remote path to local
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model', os.path.basename(model_path)))
        default_license_path = os.path.normpath(os.path.join(CURRENT_PATH, '../license', os.path.basename(license_path)))
        read_and_save_file(model_path, default_model_path)
        read_and_save_file(license_path, default_license_path)
    else:
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model/pipeline.mojo'))
        default_license_path = os.path.normpath(os.path.join(CURRENT_PATH, '../license/license.txt'))
    os.environ['DRIVERLESS_AI_LICENSE_FILE'] = default_license_path
    MODEL = daimojo.model(default_model_path)

    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = MojoModelWrapper(host="0.0.0.0")
    app.run()
