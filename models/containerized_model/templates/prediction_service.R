"
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"

library(caret)
library(plumber)
library(yaml)
library(jsonlite)

# load the necessary model packages for predict method to be available
# for example to load randomForest pakcage un-comment below line
# library(randomForest)


## below section creates a web service endpoint and
## invokes function (`calculate_prediction`) to return model predictions when endpoint is invoked

## load model and artifacts from disk
model <<- readRDS(file = '../model/model.rds')

## load metadata file containing column names
metadata <<- yaml.load_file('../model/metadata.yml')

if (length(metadata$columns) == 0) {
  print('columns list empty in metadata.yml')
  quit(status = 400)

}

#' Return "service health"
#' @get /health
#' @serializer html
function(req,res){
  res$status <- 200
  return("OK")

}

#' @post /predict
#' @serializer html
calculate_prediction <- function(payload, res) {
  tryCatch(
  {
    ## payload should contain "instances", which is a list of vectors of inputs,
    ## test data doesn't need the ground truth for prediction
    ## make sure only the features needed by model for prediction are passed
    ## here colnames(data)[-21] is used so as to map request data to first 20 feature cols
    ## response should be structured as {"payload": { "predictions": [list of predictions] } }
    test_data <- as.data.frame(payload)
    colnames(test_data) <- metadata$columns
    # predict and return results

    # if no encoder is present call predict on test data directly
    if (is.null(model$encoder)) {
      pred <- as.numeric(predict(model$model, newdata = test_data))
    }
    else if (!is.null(model$encoder) && is.null(model$artifacts)) {
      pred <- as.numeric(predict(model$model, newdata = model$encoder(test_data)))
    }
    else {
      pred <- as.numeric(predict(model$model, newdata = model$encoder(test_data, model$artifacts)))
    }
    # create response json { "payload" : {"predictions" : pred} }
    pred_list <<- list(payload = list(predictions = pred))
    pred_json <<- toJSON(pred_list)
    res$status <- 200
    return(pred_json)
  },
    # handle error and return error message
    # create error response as {"payload":{"error": ["error message"]} }
    error = function(cond) {
      error_list <<- list(payload = list(error = cond))
      error_json <<- toJSON(error_list, force = TRUE)
      res$status <- 500 # Internal Server errror in predicts
      return(error_json)
    }


  )
}

