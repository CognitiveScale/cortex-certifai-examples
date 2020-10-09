import numpy as np
# This encoder works round an issue (fix in progress) where Certifai is converting ints to floats
# The symptom of this issue is that some counterfactuals appear to have no changed features
# All the fields in this example should be ints
class Encoder:
  def __call__(self, predictions):
    return np.rint(predictions)
