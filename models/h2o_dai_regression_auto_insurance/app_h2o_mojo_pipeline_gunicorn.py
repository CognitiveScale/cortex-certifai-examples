"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper


class ModelWrapper(SimpleModelWrapper):
    """
    This example requires Certifai version 1.3.6 or later.
    """

    @staticmethod
    def __get_columns():
        """
        `__get_columns` is user defined helper method to list column names in
        order to create the dataframe for the model
        **Note**: To work with the gunicorn server (production option)
        all user defined methods must be declared inside the class as `instance methods`,
        i.e. in this example, all methods must be declared inside the
        `ModelWrapper` class and referenced using `self`

        :return: list of column names
        """
        columns = ['State Code',
                   'Claim Amount',
                   'Coverage',
                   'Education',
                   'EmploymentStatus',
                   'Gender',
                   'Income',
                   'Location Code',
                   'Marital Status',
                   'Monthly Premium Auto',
                   'Months Since Last Claim',
                   'Months Since Policy Inception',
                   'Number of Open Complaints',
                   'Number of Policies',
                   'Policy',
                   'Claim Reason',
                   'Sales Channel',
                   'Vehicle Class',
                   'Vehicle Size']
        return columns

    def set_global_imports(self):
        """
        overridden method to make external global imports
        When using external imports override the method to provide necessary imports.
        Make sure to mark them `global` to
        be used by certifai interpreter correctly. set once, use throughout.
        :return: None
        """
        global dt
        import datatable as dt

    def __get_prediction(self, preds):
        """
        For a regression model, _get_prediction should return the first and only
        prediction value.
        """
        # for regression we get only one prediction
        return preds[0]

    def predict(self, npinstances):
        # reference model by using `self.model`
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=self.__get_columns())
        predictions = self.model.predict(input_dt).to_pandas().apply(self.__get_prediction, axis=1)
        return predictions.values


if __name__ == "__main__":
    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = ModelWrapper(host="0.0.0.0", model_type='h2o_mojo', model_path='./pipeline.mojo')
    app.run(log_level="warning", production=True, num_workers=3)
