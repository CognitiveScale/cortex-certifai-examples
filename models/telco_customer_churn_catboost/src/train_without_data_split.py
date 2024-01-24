"""
An example Telco customer churn model which uses Certifai's CatEncoder
"""
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn import model_selection
import pickle

from certifai.common.utils.encoding import CatEncoder


def train(X_train, y_train):
    print('Training the model:')
    print(X_train.shape)
    print(y_train.shape)
    model = CatBoostClassifier(logging_level='Silent')
    model.fit(X_train, y_train)
    kfold = model_selection.KFold(n_splits=10, random_state=None)
    cv_acc_results = model_selection.cross_val_score(model, X_train, y_train, 
                                                     cv=kfold, 
                                                     scoring='accuracy')
    accuracy = round(cv_acc_results.mean()*100, 2)
    return model, accuracy


def main():
    cat_columns = [
        'DeviceProtection',
        'ReferredaFriend',
        'customerID',
        'Married',
        'Offer',
        'TechSupport',
        'SatisfactionScore',
        'StreamingMusic',
        'LatLong',
        'InternetService',
        'Under30',
        'SeniorCitizen',
        'OnlineBackup',
        'Dependents',
        'OnlineSecurity',
        'StreamingMovies',
        'ChurnReason',
        'StreamingTV',
        'Country',
        'Partner',
        'PaymentMethod',
        'gender',
        'PaperlessBilling',
        'State',
        'ChurnCategory',
        'PremiumTechSupport',
        'UnlimitedData',
        'Contract',
        'MultipleLines',
        'PhoneService',
        'CustomerStatus',
        'City'
    ]

    # Reads the training data directly without splitting it into train and test
    df = pd.read_csv('./datasets/train_dataset.csv')

    outcome_column = 'Churn'

    # Separate outcome
    y = df[outcome_column]
    x = df.drop(outcome_column, axis=1)

    # Train and test split
    # X_train, X_test, y_train, y_test = train_test_split(x, y, train_size=0.8, 
                                                    # random_state = 1)

    encoder = CatEncoder(cat_columns, x, normalize=True)
    encoded_x_train = encoder(x.values)
    
    # Model training
    model, accuracy = train(encoded_x_train, y)

    # Save Model
    model_object = {'model': model, 'encoder': encoder}
    modelFilePath = './model/model.pkl'
    pickle.dump(model_object, open(modelFilePath, 'wb'))
    print(f'Model saved at: ${modelFilePath}')
    

if __name__ == '__main__':
    main()
