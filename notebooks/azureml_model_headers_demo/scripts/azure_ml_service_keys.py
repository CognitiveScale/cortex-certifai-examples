# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
import random
from sklearn.externals import joblib
import sklearn as sklearn_version_test
assert sklearn_version_test.__version__ == '0.20.3', 'scikit-learn version mismatch, `pip install scikit-learn==0.20.3` to install right sklearn version for this notebook'
assert np.__version__                   == '1.16.2', 'numpy version mismatch, `pip install numpy==1.16.2` to install right numpy version for this notebook'
import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join('./')))
from scripts.cat_encoder import CatEncoder

resource_name_suffix = str(datetime.date(datetime.now()))

def main(args):
    # ###  load data in dataframe
    # load the dataset into memory
    df = pd.read_csv('data/german_credit_eval.csv')

    # ### define features 

    # %%
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

    label_column = 'outcome'

    # ### separate features and target variable

    y = df[label_column]
    X = df.drop(label_column, axis=1)

    # ### split dataset into the training and test set

    # %%
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    # %%
    encoder = CatEncoder(cat_columns, X)
    def build_model(data, name, model_family, test=None):
        if test is None:
            test = data
            
        if model_family == 'SVM':
            parameters = {'kernel':('linear', 'rbf', 'poly'), 'C':[0.1, .5, 1, 2, 4, 10], 'gamma':['auto']}
            m = svm.SVC()
        elif model_family == 'logistic':
            parameters = {'C': (0.5, 1.0, 2.0), 'solver': ['lbfgs'], 'max_iter': [1000]}
            m = LogisticRegression()
        model = GridSearchCV(m, parameters, cv=3)
        model.fit(data[0], data[1])

        # Assess on the test data
        accuracy = model.score(test[0], test[1].values)
        print(f"Model '{name}' accuracy is {accuracy}")
        return model

    svm_model_name      = f'german_credit_svm_{resource_name_suffix}'
    logistic_model_name = f'german_credit_logit_{resource_name_suffix}'

    print('Building svm model')
    svm_model = build_model((encoder(X_train.values), y_train),
                            svm_model_name,
                            'SVM',
                            test=(encoder(X_test.values), y_test))
    
    print('Building logistic model')
    logistic_model = build_model((encoder(X_train.values), y_train),
                            logistic_model_name,
                            'logistic',
                            test=(encoder(X_test.values), y_test))

    def dump_model(model_name,model_obj,encoder_obj=encoder):
        model_path = f'{model_name}.pkl'
        model_obj = {
            "model":model_obj,
            "encoder":encoder_obj
        }
        joblib.dump(value=model_obj, filename=model_path)
        print(f'model saved on disk {model_obj}')
        return model_path

    # persist models to disk
    svm_model_disk_path      = dump_model(svm_model_name,svm_model)
    print(f'persisted svm model to disk at {svm_model_disk_path}')
    logistic_model_disk_path = dump_model(logistic_model_name,logistic_model)
    print(f'persisted logistic model to disk at {logistic_model_disk_path}')

    from azureml.core import Workspace
    if args.az_config:
        az_conf_path = args.az_config
    ws = Workspace.from_config(path=az_conf_path)

    from azureml.core.model import Model

    print(f'Registering Logistic model to Azure with name {logistic_model_name}')
    logistic_model_azure = Model.register(model_path=logistic_model_disk_path,
                        model_name=logistic_model_name,
                        tags={'area': "banking credit risk", 'type': "classification"},
                        description="Logistic Classifier model to predict credit loan approval",
                        workspace=ws)
    print(f'Registering SVM model to Azure with name {svm_model_name}')
    svm_model_azure = Model.register(model_path=svm_model_disk_path,
                        model_name=svm_model_name,
                        tags={'area': "banking credit risk", 'type': "classification"},
                        description="Support Vector Machine Classifier model to predict credit loan approval",
                        workspace=ws)

    # %%

    print('Creating Azure ML Environment with the following content')
    with open("myenv.yml", 'r') as f:
        print(f.read())


    # %%
    from azureml.core.conda_dependencies import CondaDependencies
    from azureml.core.environment import Environment

    environment = Environment("german-credit-env")
    environment.python.conda_dependencies = CondaDependencies("myenv.yml")
    environment.register(workspace=ws)


    # %%
    from azureml.core.model import InferenceConfig
    from azureml.core import Webservice
    from azureml.exceptions import WebserviceException
    from azureml.core.webservice import AciWebservice

    inference_config_logistic = InferenceConfig(entry_script="logistic_score.py",
                                    environment=environment,source_directory="scripts")
    inference_config_svm = InferenceConfig(entry_script="svm_score.py",
                                    environment=environment,source_directory="scripts")

    logistic_service_name = f'german-cred-logis-svc-{resource_name_suffix}'
    svm_service_name = f'german-cred-svm-svc-{resource_name_suffix}'

    aci_deployment_config = AciWebservice.deploy_configuration(auth_enabled=True)

    # # Remove any existing services under the same name.
    # try:
    #     Webservice(ws, logistic_service_name).delete()
    # except WebserviceException:
    #     pass

    # try:
    #     Webservice(ws, svm_service_name).delete()
    # except WebserviceException:
    #     pass

    print(f'Registering Webservice for {logistic_model_name} with name {logistic_service_name}')
    service_logistic = Model.deploy(ws,
        logistic_service_name, 
        [logistic_model_azure], inference_config=inference_config_logistic,deployment_config=aci_deployment_config)

    print(f'Registering Webservice for {svm_model_name} with name {svm_service_name}')
    service_svm      = Model.deploy(ws,
        svm_service_name,
        [svm_model_azure],
        inference_config=inference_config_svm,     deployment_config=aci_deployment_config)

    service_logistic.wait_for_deployment(show_output=True)
    service_svm.wait_for_deployment(show_output=True)

    service_logistic_uri  = service_logistic.scoring_uri
    service_logistic_keys = service_logistic.get_keys()

    service_svm_uri       = service_svm.scoring_uri
    service_svm_keys      = service_svm.get_keys()

    print('The models and services created by this script will continue running until deleted. If youre following another notebook and ran this script as part of that tutorial, wait till you"ve finished the notebook before cleaning up the resources generated by this notebook')

    print('========Azure Resources to be cleaned up later=======')
    print('Azure Resource Metadata')
    print(f'Workspace / ML Resource Name  --> {ws.name}')
    print(f'Subscription ID               --> {ws.subscription_id}')
    print(f'Resource Group                --> {ws.resource_group}')
    print(f'SVM Resources                 --> {svm_model_name} | {svm_service_name}')
    print(f'Logistic Regression Resources --> {logistic_model_name} | {logistic_service_name}')

    print('You need to take the following values and input them into your Azure Certifai Pro tutorial notebook')
    print(f'service_logistic_uri - {service_logistic_uri}')
    print(f'service_logistic_key - {service_logistic_keys[0]}')

    print(f'service_svm_uri - {service_svm_uri}')
    print(f'service_svm_key - {service_svm_keys[0]}')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate Azure ML Hosted model URIs and Service Keys')
    parser.add_argument('--az_config', default='config.json', help='Path to the workspace config.json for your Azure Machine Learning Resource. Defaults to ./config.json')

    args = parser.parse_args()
    print(args)
    main(args)