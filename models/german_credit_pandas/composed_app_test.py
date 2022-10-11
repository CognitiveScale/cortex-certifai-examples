"""
Copyright (c) 2022. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import requests

test_msg = {
    "payload": {
        "instances": [
            [
                "... < 0 DM",
                6,
                "critical account/ other credits existing (not at this bank)",
                "radio/television",
                1169,
                "unknown/ no savings account",
                ".. >= 7 years",
                4,
                "male : single",
                "others - none",
                4,
                "real estate",
                "> 25 years",
                "none",
                "own",
                2,
                "skilled employee / official",
                1,
                "phone - yes, registered under the customers name",
                "foreign - yes"
            ]
        ]
    }
}

r = requests.post('http://127.0.0.1:8551/german_credit_dtree/predict', json=test_msg)
print(f'Response from dtree/predict: [{r.status_code}] {r.text}')

r = requests.post('http://127.0.0.1:8551/german_credit_logit/predict', json=test_msg)
print(f'Response from logit/predict: [{r.status_code}] {r.text}')

r = requests.post('http://127.0.0.1:8551/german_credit_mlp/predict', json=test_msg)
print(f'Response from mlp/predict: [{r.status_code}] {r.text}')

r = requests.post('http://127.0.0.1:8551/german_credit_svm/predict', json=test_msg)
print(f'Response from svm/predict: [{r.status_code}] {r.text}')

r = requests.get('http://127.0.0.1:8551/health', json=test_msg)
print(f'Response from health: [{r.status_code}] {r.text}')

r = requests.post('http://127.0.0.1:8551/shutdown', json=test_msg)
print(f'Response from shutdown: [{r.status_code}] {r.text}')
