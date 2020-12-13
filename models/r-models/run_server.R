"
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"

if (!require(caret)) {
  install.packages("plumber")
}

library(plumber)
pr <- plumber::plumb("predict_german_credit.R")
pr$run(port=8551)