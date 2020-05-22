
import numpy as np
import xgboost as xgb

class TransformedPredict:
    def __init__(self,model,dropped_indexes_list):
        self.model = model
        
    def predict(self,arr):
        dtest = xgb.DMatrix(data=np.delete(arr, self.dropped_indexes_list,1))
        return self.model.predict(dtest)
        
