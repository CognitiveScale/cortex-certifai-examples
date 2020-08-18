class Encoder:
    def __init__(self, X, target_encoded_cols):
        self.indx = [X.columns.get_loc(c) for c in target_encoded_cols]
    
    def __call__(self,X):
        X[:,self.indx] = X[:,self.indx].astype(float)
        return X
