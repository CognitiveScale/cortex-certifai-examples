import json
import sys
import random
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from utils.train_utils import Encoder
from utils.encode_decode import pickle_model

RANDOM_SEED = 0


def train():
    # for reproducible training
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    training_data_uri = "data/german_credit_eval.csv"
    save_model_as = "logistic_regression"

    data = pd.read_csv(training_data_uri)

    # Separate outcome
    y = data["outcome"]
    X = data.drop("outcome", axis=1)

    # create encoder on entire dataset
    scaler = Encoder()
    scaler.fit(X)

    # apply encoding to train and test data features
    # applied on test data to calculate accuracy metric
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=0)

    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    # start model training
    logit = LogisticRegression(random_state=RANDOM_SEED, solver="lbfgs", max_iter=1000)
    logit.fit(X_train.values, y_train.values)
    logit_acc = logit.score(X_test.values, y_test.values)
    model_binary = f"models/{save_model_as}.pkl"
    pickle_model(
        logit, scaler, "LR", logit_acc, "Logistic Regression Classifier", model_binary
    )
    print(logit_acc)
    return f"model: {model_binary}"

if __name__ == "__main__":
    print(train())