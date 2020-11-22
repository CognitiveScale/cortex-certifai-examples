"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper
from certifai.common.file.locaters import make_generic_locater
from certifai.common.file.interface import FilePath

import os
import yaml

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


class MojoModelWrapper(SimpleModelWrapper):
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
        if len(self.columns) == 0:
            raise Exception('Columns can not be empty. Please update "columns"'
                + ' in metadata.yml or prediction_service.py file.')
        SimpleModelWrapper.__init__(self, *args, **kwargs)


    def set_global_imports(self):
        """
        overridden method to make external global imports
        When using external imports override the method to provide necessary imports.
         Make sure to mark them `global` to be used by certifai interpreter correctly.
         Set once, use throughout.
        :return: None
        """
        global dt
        import datatable as dt

    def _try_as_int(self, val):
        try:
            return int(val)
        except ValueError:
            return val

    def predict(self, npinstances):
        """
        Calls predict on the H2O Mojo model, applying the get_prediction
        transform to map the H2O predictions to the expected format for the
        Certifai predict API.
        """
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=self.get_columns())
        if self.outcomes is None or len(outcomes) == 0:
            largest = preds.idxmax() # index label of largest value
            self.outcomes = self._try_as_int(largest.rsplit('.', 1)[1])
        get_preds = lambda preds: self.get_prediction(preds, self.outcomes)
        predictions = self.model.predict(input_dt).to_pandas().apply(get_preds, axis=1)
        return predictions.values

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
                raise Exception('No outcome labels provided for classification' +
                    ' model. Please update "outcomes" in metadata.yml.')
            index = preds.argmax() # position of largest value
            return outcomes[index]

        raise Exception('No prediction returned by model')

if __name__ == "__main__":
    model_path = os.getenv('MODEL_PATH')
    license_path = os.getenv('H2O_LICENSE_PATH')
    default_metadata_path = os.path.normpath(os.path.join(CURRENT_PATH,
        '../model/metadata.yml'))
    metadata_path = os.getenv('METADATA_PATH', default_metadata_path)
    if model_path is not None:
        # Copy files from remote path to local
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH,
            '../model', os.path.basename(model_path)))
        default_license_path = os.path.normpath(
            os.path.join(CURRENT_PATH, '../license', os.path.basename(license_path)))
        read_and_save_file(model_path, default_model_path)
        read_and_save_file(license_path, default_license_path)
    else:
        # allows local testing
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH,
            '../model/pipeline.mojo'))
        default_license_path = os.path.normpath(os.path.join(CURRENT_PATH,
            '../license/license.txt'))
    os.environ['DRIVERLESS_AI_LICENSE_FILE'] = default_license_path

    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = MojoModelWrapper(
        host="0.0.0.0",
        model_type='h2o_mojo',
        model_path=default_model_path,
        metadata=read_yaml(metadata_path)
    )
    app.set_global_imports() # needed if not running in production mode
    # Production mode requires Certifai 1.3.6 or higher
    app.run(production=True, log_level='warning', num_workers=3)
    # Replace above with following to run in development mode
    # app.run()
