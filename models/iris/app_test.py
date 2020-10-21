"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import requests

test_msg = {
    "payload": {
        "instances": [
            [5.1, 3.5, 1.4, 0.2],
            [6.9, 3.5, 5.5, 0.2],
            [7.7, 3.0, 6.1, 2.3]
        ]
    }
}

if __name__ == "__main__":
    r = requests.post('http://127.0.0.1:8551/predict', json=test_msg)
    print(f'Response from model: [{r.status_code}] {r.text}')
    r = requests.post('http://127.0.0.1:8551/shutdown', json=test_msg)
    print(f'Response from shutdown: [{r.status_code}] {r.text}')
