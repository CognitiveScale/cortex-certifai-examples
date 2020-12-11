"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import requests

test_msg = {
    "payload": {
		"instances": [
			"NE",
			555.6529096233675,
			"Basic",
			"Bachelor",
			"Employed",
			"F",
			57920.0,
			"Urban",
			"Divorced",
			74.0,
			6.0,
			69.0,
			0.0,
			3.0,
			"Personal L1",
			"Hail",
			"Branch",
			"Four-Door Car",
			"Medsize"
		]
    }
}

if __name__ == "__main__":
    r = requests.post('http://127.0.0.1:8551/predict', json=test_msg)
    print(f'Response from model: [{r.status_code}] {r.text}')
