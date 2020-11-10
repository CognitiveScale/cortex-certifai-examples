"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import requests

test_msg = {
    "payload": {
        "instances": [
            [
                25,
                "workclass_Private",
                226802,
                "education_11th",
                7,
                "marital-status_Never-married",
                "occupation_Machine-op-inspct",
                "relationship_Own-child",
                "race_White",
                "gender_Male",
                0,
                0,
                40,
                "native-country_United-States"
            ]
        ]
    }
}

if __name__ == "__main__":
    r = requests.post('http://127.0.0.1:8551/predict', json=test_msg)
    print(f'Response from model: [{r.status_code}] {r.text}')
