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
        SimpleModelWrapper.__init__(self, *args, **kwargs)

    def get_columns(self):
        """
        get_columns lists column names in order to re-create the dataframe for prediction
        **Note**:  must be declared inside the class as instance methods and referenced
        using `self.` to enable production mode.
            pass

        :return: list of column names
        """
        columns = [] # Fill in the list of columns - this will be used if no metadata
        cols_from_metadata = self.metadata.get('columns')
        if cols_from_metadata is not None:
            columns = cols_from_metadata

        if not len(columns) == 0:
            return columns
        raise Exception('Columns can not be empty. Please update columns in metadata.yml or prediction_service.py file.')

    def get_outcomes(self):
        """
        get_outcomes lists classification outcome class labels.
        **Note**:  all methods used in predict must be declared inside the
        class as instance methods and referenced using `self.` to enable production mode.

        :return: list of outcome class labels
        """
        outcomes = [] # Outcomes for a classification model
        outcomes_from_metadata = self.metadata.get('outcomes')
        if outcomes_from_metadata is not None:
            outcomes = outcomes_from_metadata
        return outcomes

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

    def get_prediction(self, preds):
        """
        For an H2O classification model, get_prediction returns the
        appropriate class label based on the class probability, based on the
        values in get_outcomes. If get_outcomes returns None or an
        empty list, get_prediction will use values inferred from the index
        labels of the returned predictions.

        For a regression model, get_prediction returns the single probability.
        """
        if len(preds) == 1:
            return preds[0] # regression
        if len(preds) > 1:
            outcomes = self.get_outcomes()
            if outcomes is None or len(outcomes) == 0:
                largest = preds.idxmax() # index label of largest value
                return self._try_as_int(largest.rsplit('.', 1)[1])
            index = preds.values.argmax() # position of largest value
            return outcomes[index]

        raise Exception('No prediction returned by H2O MOJO')

    def predict(self, npinstances):
        """
        Calls predict on the H2O Mojo model, applying the get_prediction
        transform to map the H2O predictions to the expected format for the
        Certifai predict API.
        """
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=self.get_columns())
        predictions = self.model.predict(input_dt).to_pandas().apply(self.get_prediction, axis=1)
        return predictions.values


if __name__ == "__main__":
    model_path = os.getenv('MODEL_PATH')
    license_path = os.getenv('H2O_LICENSE_PATH')
    default_metadata_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model/metadata.yml'))
    metadata_path = os.getenv('METADATA_PATH', default_metadata_path)
    if model_path is not None:
        # Copy files from remote path to local
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model', os.path.basename(model_path)))
        default_license_path = os.path.normpath(
            os.path.join(CURRENT_PATH, '../license', os.path.basename(license_path)))
        read_and_save_file(model_path, default_model_path)
        read_and_save_file(license_path, default_license_path)
    else:
        # allows local testing
        default_model_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model/pipeline.mojo'))
        default_license_path = os.path.normpath(os.path.join(CURRENT_PATH, '../license/license.txt'))
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
