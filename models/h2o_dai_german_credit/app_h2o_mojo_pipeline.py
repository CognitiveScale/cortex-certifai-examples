"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

from certifai.model.sdk import SimpleModelWrapper
import datatable as dt
import daimojo.model

model = daimojo.model("./pipeline.mojo")
print(f"Loaded {model.uuid} from ./pipeline.mojo")


def _get_prediction_class(preds):
    if preds[0] > preds[1]:
        return 1
    return 2


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


class GermanCredit(SimpleModelWrapper):
    def predict(self, npinstances):
        instances = [tuple(instance) for instance in npinstances]
        input_dt = dt.Frame(instances, names=columns)
        predictions = model.predict(input_dt).to_pandas().apply(_get_prediction_class, axis=1)
        return predictions.values


if __name__ == "__main__":
    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = GermanCredit(host="0.0.0.0")
    app.run()
