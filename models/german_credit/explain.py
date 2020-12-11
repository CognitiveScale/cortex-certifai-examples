"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import pickle
import pandas as pd

def main():

    # Load the trained model and its encoder
    with open('german_credit_dtree.pkl', 'rb') as f:
        saved = pickle.load(f)
        model = saved.get('model')
        encoder = saved.get('encoder', None)

    # Bring in test and training data.
    eval = pd.read_csv('german_credit_eval.csv')
    # Create explanation set without outcome
    explan = eval.drop('outcome',axis=1).sample(100)

    # setup the scan

    from certifai.scanner.builder import (CertifaiScanBuilder, CertifaiPredictorWrapper, CertifaiModel,
                                          CertifaiDataset, CertifaiDatasetSource,
                                          CertifaiPredictionTask, CertifaiTaskOutcomes, CertifaiOutcomeValue)

    predict_wrapper = CertifaiPredictorWrapper(model, encoder=encoder)

    task = CertifaiPredictionTask(CertifaiTaskOutcomes.classification(
        [
            CertifaiOutcomeValue(2,name='Denied'),
            CertifaiOutcomeValue(1, name='Granted', favorable=True)
        ]),
        prediction_description='Determine whether a loan is granted')

    scan = CertifaiScanBuilder.create('german_credit',
                                      prediction_task=task)
    # Add a model
    scan.add_model(CertifaiModel('dtree', local_predictor=predict_wrapper))

    # Add the eval dataset
    eval_dataset = CertifaiDataset('evaluation',
                                   CertifaiDatasetSource.dataframe(eval))
    scan.add_dataset(eval_dataset)
    scan.evaluation_dataset_id = 'evaluation'

    # Let the scanner know which field is the label/outcome
    scan.dataset_schema.outcome_feature_name = 'outcome'

    # Add explanation dataset
    explan_dataset = CertifaiDataset('explanation',
                                   CertifaiDatasetSource.dataframe(explan))

    scan.add_dataset(explan_dataset)
    scan.explanation_dataset_id = 'explanation'

    scan.add_evaluation_type('explanation')
    result = scan.run(write_reports=True)

if __name__ == "__main__":
    main()
