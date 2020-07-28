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

    # Load dataset
    data = pd.read_csv('german_credit_eval.csv')

    # Separate outcome
    y = data['outcome']
    x = data.drop('outcome',axis=1)

    # Bring in test and training data
    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state = 0)

    # Create an encoder
    cat_columns = [
        'checkingstatus',
        'history',
        'purpose',
        'savings',
        'employ',
        'status',
        'others',
        'property',
        'age',
        'otherplans',
        'housing',
        'job',
        'telephone',
        'foreign'
    ]
    encoder = CatEncoder(cat_columns, x, normalize=True)
    encoded_x_train = encoder(x_train.values)
    encoded_x_test = encoder(x_test.values)

    # Train a decision tree model
    from sklearn.tree import DecisionTreeClassifier
    dtree = DecisionTreeClassifier(criterion = 'entropy', random_state = 0)
    dtree.fit(encoded_x_train, y_train.values)
    dtree_acc = dtree.score(encoded_x_test,y_test.values)

    # Train a multi-layer perceptron model
    from sklearn.neural_network import MLPClassifier
    mlp = MLPClassifier(hidden_layer_sizes=(20,20),max_iter=2000)
    mlp.fit(encoded_x_train, y_train.values)
    mlp_acc = mlp.score(encoded_x_test,y_test.values)

    # Train a support vector machine model
    from sklearn import svm
    SVM = svm.SVC(gamma='scale')
    SVM.fit(encoded_x_train, y_train.values)
    svm_acc = SVM.score(encoded_x_test,y_test.values)

    # Train a logistic regression model
    from sklearn.linear_model import LogisticRegression
    logit = LogisticRegression(random_state=0, solver='lbfgs')
    logit.fit(encoded_x_train, y_train.values)
    logit_acc = logit.score(encoded_x_test,y_test.values)

    # function to pickle our models for later access
    def pickle_model(model, encoder, model_name, test_accuracy, description, filename):
        model_obj = {'model': model, 'encoder': encoder, 'name': model_name,
                     'description': description, 'test_acc': test_accuracy,
                     'created': int(time.time())}
        with open(filename, 'wb') as file:
            pickle.dump(model_obj, file)
        print(f"Saved: {model_name}")

    # Save models as pickle files
    pickle_model(dtree, encoder, 'Decision Tree', dtree_acc, 'Basic Decision Tree model', 'german_credit_dtree.pkl')
    pickle_model(logit, encoder, 'LOGIT', logit_acc, 'Basic LOGIT model', 'german_credit_logit.pkl')
    pickle_model(mlp, encoder, 'MLP', mlp_acc, 'Basic MLP model', 'german_credit_mlp.pkl')
    pickle_model(SVM, encoder, 'SVM', svm_acc, 'Basic SVM model', 'german_credit_svm.pkl')


if __name__ == "__main__":
    main()
