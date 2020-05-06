import os
import json
import numpy as np
from sklearn.externals import joblib
import traceback


def init():
    global model
    global encoder
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # For multiple models, it points to the folder containing all deployed models (./azureml-models)
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'german_credit_svm.pkl')
    # deserialize the model_obj file back into a sklearn model and scaler object
    model_obj  = joblib.load(model_path)
    model      = model_obj.get('model')
    encoder    = model_obj.get('encoder')


def run(data):
    try: 
        # certifai invokes model with the json schema -> {"payload": {"instances": [ [6,107,88,0,0,36.8,0.727,31], [5,100,80,0,0,31.9,0.61,33] ]}}
        data  = json.loads(data).get('payload', {}).get('instances', [])
        data  = np.array(data, dtype=object)
        data  = data if data.ndim == 2 else np.reshape(data, (1, -1))
        if encoder:
            data = encoder(data)
        result = model.predict(data)
        # you can return any datatype as long as it is JSON-serializable
        # certifai expects model response with the json schema -> {"payload": {"predictions": [1,0]} }

        return {"payload":{ "predictions": result.tolist()} }
    except Exception as e:
        error = str(e)
        print(traceback.format_exc())
        return error