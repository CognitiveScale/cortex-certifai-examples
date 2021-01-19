"
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"

model_path <- Sys.getenv("MODEL_PATH")
if (!model_path == ""){
  library("aws.s3")
  model <- save_object(file='/model/model.rds', model_path)
}

library(plumber)
pr <- plumber::plumb("/src/prediction_service.R")
pr$run(host="0.0.0.0" ,port=8551)