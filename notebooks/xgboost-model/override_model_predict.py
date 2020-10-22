
import numpy as np
import xgboost as xgb
class TransformedPredict:
    def __init__(self,model):
        self.model = model
    def predict(self,arr):
        dtest = xgb.DMatrix(data=arr)
        return self.model.predict(dtest)
