"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import requests

test_msg = {
    "payload": {
        "instances": [
            [149190, 55629189, 'Caucasian', 'Female', '[10-20)', '?', 1, 1, 7, 3, '?', '?', 59, 0, 18, 0, 0, 0, 'Other', 'Diabetes', 'Other', 9, 'None', 'None', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'Up', 'No', 'No', 'No', 'No', 'No', 'Ch', 'Yes']
        ]
    }
}

if __name__ == "__main__":
    r = requests.post('http://127.0.0.1:8551/predict', json=test_msg)
    print(f'Response from model: [{r.status_code}] {r.text}')
    # r = requests.post('http://127.0.0.1:8551/shutdown', json=test_msg)
    # print(f'Response from shutdown: [{r.status_code}] {r.text}')
