
import numpy as np
import xgboost as xgb

class TransformedPredict:
    def __init__(self,model,dropped_indexes_list):
        self.model = model
        self.dropped_indexes_list = dropped_indexes_list
        
    def predict(self,arr):
        # data = np.delete(arr, self.dropped_indexes_list,1)
        dtest = xgb.DMatrix(data=arr)
        return self.model.predict(dtest)
        
