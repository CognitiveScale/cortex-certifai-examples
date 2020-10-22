"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import time
import random
import pickle
import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from certifai.common.utils.encoding import CatEncoder
# supress all warnings
warnings.filterwarnings('ignore')


def main():
    random.seed(0)
    np.random.seed(0)

    from sklearn import datasets

    # Bring in test and training data.
    x, y = datasets.load_iris(return_X_y=True)
    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=.5)

    # Create an encoder
    cat_columns = [] # All columns are numeric
    encoder = CatEncoder(cat_columns, pd.DataFrame(x), normalize=True)
    encoded_x_train = encoder(x_train)
    encoded_x_test = encoder(x_test)

    # Train a support vector machine
    from sklearn.svm import SVC
    svm = SVC()
    svm.fit(encoded_x_train, y_train)
    svm_acc = svm.score(encoded_x_test,y_test)

    # function to pickle our models for later access
    def pickle_model(model, encoder, model_name, test_accuracy, description, filename):
        model_obj = {'model': model, 'encoder': encoder, 'name': model_name,
                     'description': description, 'test_acc': test_accuracy,
                     'created': int(time.time())}
        with open(filename, 'wb') as file:
            pickle.dump(model_obj, file)
        print(f"Saved: {model_name}")

    # Save models as pickle files
    pickle_model(svm, encoder, 'Support Vector Machine', svm_acc, 'Support Vector Machine classifier', 'iris_svm.pkl')


if __name__ == "__main__":
    main()
