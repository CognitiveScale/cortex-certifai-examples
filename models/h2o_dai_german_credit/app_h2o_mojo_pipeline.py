"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper
import datatable as dt
import daimojo.model

model = daimojo.model("./pipeline.mojo")
print(f"Loaded {model.uuid} from ./pipeline.mojo")


class GermanCredit(SimpleModelWrapper):
    @staticmethod
    def __get_columns():
        """
        `__get_columns` is user defined helper method to list column names in
        order to create the dataframe for the model
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
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=self.__get_columns())
        predictions = model.predict(input_dt).to_pandas().apply(self.__get_prediction, axis=1)
        return predictions.values


if __name__ == "__main__":
    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = GermanCredit(host="0.0.0.0")
    app.run()
