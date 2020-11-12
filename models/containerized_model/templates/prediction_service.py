"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import os
import pickle
import yaml

from certifai.model.sdk import SimpleModelWrapper
from certifai.common.file.locaters import make_generic_locater
from certifai.common.file.interface import FilePath

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def read_and_save_file(source_path, destination_path):
    if source_path is None:
        return
    # Fetch file as binary
    locater = make_generic_locater(FilePath(source_path))
    if locater.isfile():
        with locater.reader() as f:
            contents = f.read()
        with open(destination_path, 'wb') as f:
            f.write(contents)

def read_yaml(source_path):
    if source_path is None:
        return {}
    # Read file
    locater = make_generic_locater(FilePath(source_path))
    try:
        with locater.text_reader() as f:
            contents = f.read()
        return yaml.safe_load(contents)
    except FileNotFoundError:
        return {}

class Wrapper(SimpleModelWrapper):
    def __init__(self, *args, **kwargs):
        self.metadata = kwargs.pop('metadata', {})
        super(self.__class__, self).__init__(*args, **kwargs)

    def set_global_imports(self):
        """
        Override this method to make external global imports
        When using external imports override the method to provide necessary imports. Make sure to mark them `global` to
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


def main():
    model_path = os.getenv('MODEL_PATH')
    default_metadata_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model/metadata.yml'))
    metadata_path = os.getenv('METADATA_PATH', default_metadata_path)
    if model_path is not None:
        # Copy files from remote path to local
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model', os.path.basename(model_path)))
        read_and_save_file(model_path, default_model_path)
    else:
        # allows local testing
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model/model.pkl'))
    model_pickle = pickle.load(open(default_model_path, 'rb'))
    model = model_pickle.get('model')
    encoder = model_pickle.get('encoder')
    metadata = read_yaml(metadata_path)
    app = Wrapper(model=model,
                  encoder=encoder,
                  host='0.0.0.0',
                  supports_soft_scores=False, # set true for xgboost
                  threshold=None,
                  score_labels=metadata.get('outcomes'),
                  metadata=metadata
                  )
    app.set_global_imports() # needed if not running in production mode
    # Production mode requires Certifai 1.3.6 or higher
    # app.run(production=True, log_level='warning', num_workers=3)
    # Replace above with following to run in development mode
    app.run()

if __name__ == '__main__':
    main()
