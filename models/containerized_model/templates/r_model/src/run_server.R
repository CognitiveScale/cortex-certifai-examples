"
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"

bucket_access_key <- Sys.getenv("BUCKET_ACCESS_KEY")
bucket_secret_key <- Sys.getenv("BUCKET_SECRET_KEY")

Sys.setenv("AWS_ACCESS_KEY_ID" = bucket_access_key)
Sys.setenv("AWS_SECRET_ACCESS_KEY" = bucket_secret_key)

model_path <- Sys.getenv("MODEL_PATH")
downloaded_model_path <- '/model/model.rds'

if (!model_path == "") {
  library("aws.s3")
  model <- try(save_object(file = downloaded_model_path, model_path))
  err_attr <- attr(model, "condition")
  opt_msg <- grep("failed|permission", ignore.case = TRUE, err_attr$message)
  if (!is.null(err_attr) && !is.null(opt_msg)) {
    downloaded_model_path <- '/tmp/model.rds'
    print("can't persist model in container.. using /tmp")
    dir.create('/tmp', showWarnings = FALSE)
    model <- save_object(file = downloaded_model_path, model_path)
  }
}

metadata_path <- Sys.getenv("METADATA_PATH")
downloaded_metadata_path <- "/model/metadata.yml"

if (!metadata_path == "") {
  library("aws.s3")
  metadata <- try(save_object(file = downloaded_metadata_path, metadata_path))
  err_attr <- attr(metadata, "condition")
  opt_msg <- grep("failed|permission", ignore.case = TRUE, err_attr$message)
  if (!is.null(err_attr) && !is.null(opt_msg)) {
    downloaded_metadata_path <- "/tmp/metadata.yml"
    print("can't persist metadata in container., using /tmp")
    dir.create('/tmp', showWarnings = FALSE)
    metadata <- save_object(file = downloaded_metadata_path, metadata_path)
  }
}

Sys.setenv("MODEL_ON_DISK_PATH" = downloaded_model_path)
Sys.setenv("METADATA_ON_DISK_PATH" = downloaded_metadata_path)

library(plumber)
pr <- plumber::plumb("/src/prediction_service.R")
pr$run(host="0.0.0.0" ,port=8551)