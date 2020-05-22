
import numpy as np
import xgboost as xgb
class DemoEncoder:
    
    def __init__(self,drop_columns):
        self.drop_columns = drop_columns
    
    def __call__(self,x,drop=True):
        if not drop:
            return xgb.DMatrix(data=x)
        return xgb.DMatrix(data=np.delete(x, self.drop_columns,1))
