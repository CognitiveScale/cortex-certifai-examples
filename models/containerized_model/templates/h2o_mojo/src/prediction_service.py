"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper

# All user-defined code that is to be used in the prediction wrapper must be in
# instance methods in the wrapper class, or in imported modules
# defined in set_global_imports

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
        input_dt = dt.Frame(instances, names=self.columns)
        predictions = self.model.predict(input_dt).to_pandas()
        if (self.outcomes is None or len(self.outcomes) == 0) and len(predictions.columns) > 1:
            self.outcomes = [self._try_as_int(label.rsplit('.', 1)[1])
                for label in predictions.columns]
        get_preds = lambda preds: self.get_prediction(preds, self.outcomes)
        return predictions.apply(get_preds, axis=1).values

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


# These imports are used in launching the prediction service. They are not
# used within the prediction service
import os
import pickle
from utils import fetch_model, load_metadata, setup_license_file

if __name__ == "__main__":
    from pathlib import Path
    os.environ[
        "PYTHONPATH"] = str(Path.joinpath(Path(__file__).parent).resolve())

    metadata = load_metadata()
    local_model_path = fetch_model()
    setup_license_file()

    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = MojoModelWrapper(
        host="0.0.0.0",
        model_type='h2o_mojo',
        model_path=local_model_path,
        metadata=metadata
    )
    app.set_global_imports() # needed if not running in production mode
    # Production mode requires Certifai 1.3.6 or higher
    app.run(production=True, log_level='warning', num_workers=3)
    # Replace above with following to run in development mode
    # app.run()
