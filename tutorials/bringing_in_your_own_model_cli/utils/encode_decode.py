import pickle
import sys
import time

def init_model(model_name):
    print(f"loading {model_name} ")
    fl = f"models/{model_name}.pkl"
    with open(fl, "rb") as f:
        return pickle.load(f)

def pkl_path(project, model):
    return "models/{}_{}.pkl".format(project, model)


def pickle_model(model, scaler, model_name, test_accuracy, description, filename):
    model_obj = {}
    model_obj["model"] = model
    model_obj["scaler"] = scaler
    model_obj["modelName"] = model_name
    model_obj["modelDescription"] = description
    model_obj["test_acc"] = test_accuracy
    model_obj["createdTime"] = int(time.time())
    with open(filename, "wb") as file:
        pickle.dump(model_obj, file)
    print(f"Saved: {model_name}")        