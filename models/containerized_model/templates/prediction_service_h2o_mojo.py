"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper
from certifai.common.file.locaters import make_generic_locater
from certifai.common.file.interface import FilePath

import os
# import daimojo.model

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


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


class MojoModelWrapper(SimpleModelWrapper):

    def get_columns(self):
        """
        get_columns lists column names in order to re-create the dataframe for prediction
        **Note**:  must be declared inside the class as instance methods and referenced
        using `self.` to enable production mode.
            pass

        :return: list of column names
        """
        columns = [] # Fill in the list of columns
        if not len(columns) == 0:
            return columns
        raise Exception('Columns can not be empty. Please update columns in prediction_service.py file.')

    def get_outcomes(self):
        """
        get_outcomes lists classification outcome class labels in the order
        returned by H2O. If this returns an empty list, the labels will be
        inferred.
        **Note**:  all methods used in predict must be declared inside the
        class as instance methods and referenced using `self.` to enable production mode.

        :return: list of outcome class labels
        """
        outcomes = [] # Fill in the list of outcomes for a classification model
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
    metadata_path = os.getenv('METADATA_PATH')
    license_path = os.getenv('H2O_LICENSE_PATH')
    default_metadata_path = os.path.normpath(os.path.join(CURRENT_PATH, '../model/metadata.yml'))
    # read_and_save_file(metadata_path, default_metadata_path)
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
    app = MojoModelWrapper(host="0.0.0.0",
                           model_type='h2o_mojo',
                           model_path=default_model_path)
    app.set_global_imports() # needed if not running in production mode
    # Production mode requires Certifai 1.3.6 or higher
    app.run(production=True, log_level='warning', num_workers=3)
    # Replace above with following to run in development mode
    # app.run()
