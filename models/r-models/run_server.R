"
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"

library(plumber)
pr <- plumber::plumb("/src/predict_german_credit.R")
pr$run(host="0.0.0.0" ,port=8551)