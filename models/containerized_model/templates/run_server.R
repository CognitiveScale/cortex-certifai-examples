"
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"

bucket_access_key <- Sys.getenv("BUCKET_ACCESS_KEY")
bucket_secret_key <- Sys.getenv("BUCKET_SECRET_KEY")

Sys.setenv("AWS_ACCESS_KEY_ID"=bucket_access_key)
Sys.setenv("AWS_SECRET_ACCESS_KEY"=bucket_secret_key)

model_path <- Sys.getenv("MODEL_PATH")
if (!model_path == ""){
  library("aws.s3")
  model <- save_object(file='/model/model.rds', model_path)
}

metadata_path <- Sys.getenv("METADATA_PATH")
if (!metadata_path == ""){
  library("aws.s3")
  metadata <- save_object(file='/model/metadata.yml', metadata_path)
}



library(plumber)
pr <- plumber::plumb("/src/prediction_service.R")
pr$run(host="0.0.0.0" ,port=8551)