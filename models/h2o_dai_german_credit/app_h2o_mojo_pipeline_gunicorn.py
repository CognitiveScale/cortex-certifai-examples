"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper


class GermanCredit(SimpleModelWrapper):
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
        `GermanCredit` class and referenced using `self`

        :return: list of column names
        """
        columns = ['checkingstatus',
                   'duration',
                   'history',
                   'purpose',
                   'amount',
                   'savings',
                   'employ',
                   'installment',
                   'status',
                   'others',
                   'residence',
                   'property',
                   'age',
                   'otherplans',
                   'housing',
                   'cards',
                   'job',
                   'liable',
                   'telephone',
                   'foreign'
                   ]
        return columns

    def set_global_imports(self):
        """
        overridden method to make external global imports
        When using external imports override the method to provide necessary imports.
        Make sure to mark the imported dependencies as `global` to
        be used by certifai interpreter correctly. set once, use throughout.
        :return: None
        """
        global dt
        import datatable as dt


    def __get_prediction(self, preds):
        """
        `__get_prediction` is user defined helper method to convert the H2O model
        outputs to the predictions expected by Certifai. In this example,
        returns the appropriate class label based on the class probability.
        Specifically, the first label is 1 (loan granted) and the second label is 2 (loan denied)
        """
        if preds[0] > preds[1]:
            return 1
        return 2


    def predict(self, npinstances):
        # reference model by using `self.model`
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=self.__get_columns())
        predictions = self.model.predict(input_dt).to_pandas().apply(self.__get_prediction, axis=1)
        return predictions.values


if __name__ == "__main__":
    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = GermanCredit(host="0.0.0.0", model_type='h2o_mojo', model_path='./pipeline.mojo')
    app.run(log_level="warning", production=True, num_workers=3)
