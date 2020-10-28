"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper


class GermanCredit(SimpleModelWrapper):

    @staticmethod
    def __get_columns():
        """
        user defined methods need to be prefixed by __
        __get_columns is user defined helper method to list column names in
        order to re-create the dataframe for prediction

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
        When using external imports override the method to provide necessary imports. Make sure to mark them `global` to
        be used by certifai interpreter correctly. set once,use throughout.

        :return: None
        """
        global dt
        import datatable as dt

    def predict(self, npinstances):
        # reference model by using `self.model`
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=self.__get_columns())
        predictions = self.model.predict(input_dt).to_pandas().apply(lambda x: 1 if x[0] > x[1] else 2, axis=1)
        return predictions.values


if __name__ == "__main__":
    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = GermanCredit(host="0.0.0.0", model_type='h2o_mojo', model_path='model/pipeline.mojo')
    app.run(log_level="warning", production=True, num_workers=3)
