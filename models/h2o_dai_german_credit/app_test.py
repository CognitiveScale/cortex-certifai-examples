"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
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

if __name__ == "__main__":
    r = requests.post('http://127.0.0.1:8551/predict', json=test_msg)
    print(f'Response from model: [{r.status_code}] {r.text}')
