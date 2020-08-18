# coding: utf-8

# ## Building a Cortex Certifai scan programatically
# 
# In this notebook we'll build up a scan definition from first principles, against a local model trained within the notebook. We will then run that scan and save its results. 
# 
# - Load the dataset and model from disk
# - Create scan defintion using Certifai Builder Api
# - Refer to the [Cortex Certifai documentation](https://cognitivescale.github.io/cortex-certifai/docs/about) for detailed information about Cortex Certifai.
# - Refer to [Cortex Certifai Examples Github](https://github.com/CognitiveScale/cortex-certifai-examples) for more self start tutorials
# 
# *Please Note*: this notebook assumes: 
# - trained model and dataset is available within the the environment
# - Cortex Certifai toolkit and model dependencies are installed
# 

# In[1]:


import pandas as pd
# from IPython.display import display
import numpy as np
from certifai.scanner.builder import (CertifaiScanBuilder, CertifaiPredictorWrapper, CertifaiModel, CertifaiModelMetric,
                                      CertifaiDataset, CertifaiGroupingFeature, CertifaiDatasetSource,
                                      CertifaiPredictionTask, CertifaiTaskOutcomes, CertifaiOutcomeValue,
                                      CertifaiModelMetric,
                                      CertifaiFeatureDataType, CertifaiFeatureSchema, CertifaiDataSchema,
                                      CertifaiFeatureRestriction)
from certifai.scanner.report_utils import scores, construct_scores_dataframe
from certifai.common.utils.encoding import CatEncoder
import joblib

# In[2]:


# check required packages and their version
import sklearn as scikit


def start_scan():
    # In[3]:

    seed = 42
    np.random.seed(seed)

    #
    # ### Load pre-trained model from disk along with encoder (if present)
    #
    # - replace model_path variable below to point to stored model binary on disk
    #

    # In[4]:

    # load model
    model_path = 'models/german_credit_multiclass.joblib'
    print(f'loading {model_path}')
    try:
        model = joblib.load(model_path)
    except FileNotFoundError as e:
        print(f'model `{model_path}` not found. Looks like model has not been trained or file location is wrong')
        raise Exception(str(e))
    print(model)

    # In[5]:

    base_path = '../..'
    all_data_file = f"{base_path}/datasets/german_credit_eval_multiclass_encoded.csv"

    df = pd.read_csv(all_data_file)

    one_hot_encoded_cat_cols = [
        'checkingstatus',
        'others',
        'age',
        'job',
        'employ',
        'property',
        'foreign',
        'history',
        'savings',
        'purpose',
        'housing'
    ]

    target_encoded_cat_cols = ['otherplans', 'status', 'telephone']
    value_encoded_cat_cols = []
    label_column = 'outcome'

    # In[6]:

    # currently Certifai doesn't natively support TargetEncoded categoricals features,
    # built-in support will be added in the next release
    # this is a workaround for time being
    # for Certifai to deal with floating point categoricals(target encoded),
    # we need to covert targeted encoded cols to string
    # we will be passing this dataframe to certifai for evaluation(see Adding Certifai Evaluation section below)

    df_st = df.copy()
    decimals = 3
    df_st[target_encoded_cat_cols] = df[target_encoded_cat_cols].apply(lambda x: round(x, decimals)).astype(str)

    # ###  target_encoded string categorical to floating point encoding

    # In[7]:

    # get_ipython().run_cell_magic('writefile', 'encoder.py', 'class Encoder:\n    def __init__(self, X, target_encoded_cols):\n        self.indx = [X.columns.get_loc(c) for c in target_encoded_cols]\n    \n    def __call__(self,X):\n        X[:,self.indx] = X[:,self.indx].astype(float)\n        return X')

    # In[8]:

    # create the encoder callable(on the new dataFrame) to be passed to certifai
    # this is to convert target_encoded strings in new dataframe back to floating points
    # since model is trained on target encoded features(floating points)
    from encoder import Encoder

    y = df_st[label_column]
    X = df_st.drop(label_column, axis=1)
    encoder = Encoder(X, target_encoded_cat_cols)

    # ### Load Dataset and create one-hot feature-value mappings dict
    #
    # - our dataset has one-hot feature values encoded as dataset columns along with target_encoded categoricals
    # - these one-hot encoded features present as column have column names delimited using `_` e.g. `age_<= 25 years`  `age_> 25 years` etc.
    # - we create one hot value mappings for each  one-hot encoded feature below
    # (e.g. `feature`: {`column_name_correponding_to_feature`: `features_value_in_column_for_given_feature`} )
    #     ```
    #     'age': {'age_<= 25 years': '<= 25 years',
    #     'age_> 25 years': '> 25 years'}
    #    ```
    # - `one_hot_value_mappings` created above will be used later used to create `CertifaiDatasetSchema`
    # > **Please Note**: this is only needed in-case dataset already has one-hot encoded feature as columns. Also if you already have the persisted mappings with same schema you can use that as well

    # In[9]:

    from collections import defaultdict

    mappings = defaultdict(list)
    for col in df_st.columns.to_list():
        col_list = []
        feature_name, feature_value = col.split('_')[0], col.split('_')[1:]
        if feature_name in one_hot_encoded_cat_cols:
            if feature_value:
                mappings[feature_name].append('_'.join(feature_value))

    # create a mapping from {feature -> {1-hot_column_name_in_csv: feature_value }} using the feature `mapping` list

    """
    workclass:
         workclass_Local-gov -> Local-gov
         workclass_Self-emp-inc -> Self-emp-inc
    """
    one_hot_value_mappings = {}
    for k, v in mappings.items():
        one_hot_value_mappings[k] = {f'{k}_{cols}': cols for cols in v}

    # ### Construct target encoder mappings
    # - to generate target_mappings using `category_encoders.target_encoder.TargetEncoder` (from category-encoders package) `te` object we can use the below snippet
    # ```
    # target_mappings = {}
    # for feature in target_encode_cat_cols:
    #     feature_mappings = {}
    #     for ordinal_mapping in te.ordinal_encoder.category_mapping:
    #         if ordinal_mapping['col'] == feature:
    #             mapping = ordinal_mapping['mapping']
    #             for idx, ordinal in enumerate(mapping):
    #                 label = mapping.index[idx]
    #                 if not (isinstance(label, float) and np.isnan(label)):
    #                     feature_mappings[label] = te.mapping[feature][ordinal]
    #             break
    #     target_mappings[feature] = feature_mappings
    # ```

    # In[10]:

    # above cell demonstrates how to create the mappings
    # we use the persisted value mappings created using same code from above
    # we also get the target_encoded mappings
    import json

    with open('../dataset_generation/cat_mappings.json', 'r') as fl:
        mappings = json.load(fl)
    print(mappings.keys())
    one_hot_value_mappings = mappings.get('one_hot_encoded_mappings')
    target_mappings = mappings.get('target_encoded_mappings')
    print(f'---------\ntarget encoded value mappings ->\n{target_mappings}')

    # ## Certifai Evaluation Setup

    # ### create Certifai model proxy
    #
    # - [CertifaiPredictorWrapper](https://cognitivescale.github.io/cortex-certifai/certifai-api-ref-1.3.2/certifai.scanner.builder.html?highlight=certifaipredictorwrapper#certifai.scanner.builder.CertifaiPredictorWrapper) api is used to wrap model objects with encoder/decoder callables
    # - if model has encoding, decoding capabilities built into it, `encoder`/`decoder` kwargs need not be provided

    # In[11]:

    model_proxy = CertifaiPredictorWrapper(model, encoder=encoder)

    # ### test wrapped model_proxy predicts

    # In[12]:

    # # test to assert wrapped certifai model predicts == raw model predicts
    assert (model_proxy.model.predict(encoder(X[:10].values)) ==
            model.predict(df.drop(label_column, axis=1)[:10].values)).all

    print(f'accuracy workaround is {model.score(X, y)}')

    #
    # ### define  Certifai task type
    #
    # - CertifaiTaskOutcomes : Cortex Certifai supports classification as well as regression models. Here we have an example of multiclass classificaton (e.g. Determine whether a loan should be granted)
    # - CertifaiOutcomeValue : define the outcomes possible from the model predictions. here we have a multiclass classification model that predicts whether loan will be
    # - `granted`,
    # - `denied` or sent for
    # - `further inspection`
    #
    #
    # Note: Please refer to Certifai Api [docs](https://cognitivescale.github.io/cortex-certifai/certifai-api-ref/certifai.scanner.builder.html) for more details

    # In[13]:

    # Create Certifai evaluation task and add that to scan object
    # First define the possible prediction outcomes

    task = CertifaiPredictionTask(CertifaiTaskOutcomes.classification(
        [
            CertifaiOutcomeValue(1, name='Loan granted', favorable=True),
            CertifaiOutcomeValue(2, name='Loan denied', favorable=False),
            CertifaiOutcomeValue(3, name='further inspection', favorable=False)
        ],
        favorable_outcome_group_name='Loan Granted',
        unfavorable_outcome_group_name='Loan Denied or subject to futher inspection'
    ),

        prediction_description='Determine whether a loan should be granted')

    scan = CertifaiScanBuilder.create('german_credit_te_multiclass_workaround',
                                      prediction_task=task)

    # ### add the model to be evaluated from above

    # In[14]:

    first_model = CertifaiModel('german_credit_multiclass', local_predictor=model_proxy)
    scan.add_model(first_model)

    # ### create `CertifaiFeatureSchema` using categorical mappings dict from above
    #
    # - for one-hot encoded features we use `one_hot_value_mappings` from above to let Certifai know the different features values along with data types for that particular feature
    # - for target encoded and value encoded features we let Certifai know their unique sets of values
    # - define [CertifaiFeatureDataType](https://cognitivescale.github.io/cortex-certifai/certifai-api-ref-1.3.2/certifai.scanner.builder.html?highlight=certifaifeaturedatatype#certifai.scanner.builder.CertifaiFeatureDataType) for categorical features
    # - define [CertifaiFeatureSchema](https://cognitivescale.github.io/cortex-certifai/certifai-api-ref-1.3.2/certifai.scanner.builder.html?highlight=certifaifeatureschema#certifai.scanner.builder.CertifaiFeatureSchema) for the datatype created above
    # - add the schema to [CertifaiDataSchema](https://cognitivescale.github.io/cortex-certifai/certifai-api-ref-1.3.2/certifai.scanner.builder.html?highlight=certifaidataschema#certifai.scanner.builder.CertifaiDataSchema)

    # In[15]:

    cat_features = []
    for feature in one_hot_encoded_cat_cols + target_encoded_cat_cols + value_encoded_cat_cols:
        if feature in one_hot_value_mappings:
            data_type = CertifaiFeatureDataType.categorical(value_columns=one_hot_value_mappings[feature].items())
            feature_schema = CertifaiFeatureSchema(name=feature,
                                                   data_type=data_type)
            cat_features.append(feature_schema)

        elif feature in target_encoded_cat_cols:
            data_type = CertifaiFeatureDataType.categorical(
                values=sorted(list(map(lambda x: str(round(x, decimals)), target_mappings[feature].values()))))
            feature_schema = CertifaiFeatureSchema(name=feature,
                                                   data_type=data_type)
            cat_features.append(feature_schema)
        elif feature in df_st.columns:
            print(feature)
            data_type = CertifaiFeatureDataType.categorical(values=sorted(df_st[feature].unique().tolist()))
            feature_schema = CertifaiFeatureSchema(name=feature,
                                                   data_type=data_type)
            cat_features.append(feature_schema)

    # certifai dataset schema combining numerical categorical features and 1-hot features
    schema = CertifaiDataSchema(features=cat_features)
    scan.dataset_schema = schema

    # ### Add Certifai Evaluation

    # In[16]:

    # certifai evaluation setup

    # Add the explanation dataset. Here we run explanations for first 100 rows from the dataset

    # expn_dataset = CertifaiDataset('explanation',
    #                                CertifaiDatasetSource.dataframe(df_st[:100]))
    # scan.add_dataset(expn_dataset)
    # scan.explanation_dataset_id = 'explanation'

    # add the evaluation for performance, explainability, robustness, fairness
    # scan.add_evaluation_type('explanation')
    scan.add_evaluation_type('explainability')
    # scan.add_evaluation_type('robustness')
    # scan.add_evaluation_type('fairness')
    # scan.add_metric(CertifaiModelMetric('accuracy', certifai_metric='accuracy'))
    # scan.atx_performance_metric = 'accuracy'
    # scan.add_evaluation_type('performance')

    # add fairness features

    # set fairness features
    fairness_fields = ['status', 'age']

    for feature in fairness_fields:
        scan.add_fairness_grouping_feature(CertifaiGroupingFeature(feature))

    # add the evaluation dataset from dataframe loaded at the start of the notebook
    eval_dataset = CertifaiDataset('evaluation',
                                   CertifaiDatasetSource.dataframe(df_st))
    scan.add_dataset(eval_dataset)
    scan.evaluation_dataset_id = 'evaluation'
    # scan.test_dataset_id = 'evaluation'

    # ### specify target column if present in dataset

    # In[17]:

    # since dataset has ground truth or `target` variable present in it we let certifai know of the outcome column
    scan.dataset_schema.outcome_feature_name = label_column

    # ### Initiate scan

    # In[18]:

    # start the scan
    result = scan.run(base_path='.', write_reports=True)


if __name__ == '__main__':
    start_scan()
