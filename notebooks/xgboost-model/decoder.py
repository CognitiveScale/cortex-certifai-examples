import numpy as np

class Decoder:
    def __init__(self,threshold):
        self.threshold = threshold
    
    def __call__(self,x):
        if not isinstance(x, np.ndarray):
             x = np.array(x)
        return (x > self.threshold).astype(int)
