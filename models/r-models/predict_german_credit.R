# predict_german_credit.R


#jsonlite is needed for dealing with json request
if (!require(jsonlite)) {
  install.packages("jsonlite")
}
#plumber is needed for creating the service api
if (!require(plumber)) {
  install.packages("plumber")
}

library(caret)
library(randomForest)
library(plumber)


## below section creates a web service endpoint and
## invokes function (`calculate_prediction`) to return model predictions when endpoint is invoked

## load model and artifacts from disk
model.list <<- readRDS(file = 'german_credit_rf.rds')

## filter bad request with ill-fromed schema
#' @filter badrequest
function(req, res) {
  if (is.null(fromJSON(req$postBody)$payload$instances))
  {
    res$status <- 400 # Bad Request
    return(list(error = "Missing `instances` key"))
  }
  else {
    plumber::forward()
  }
}
#' predict '1 (loan granted)/2 (loan denied)' for set of inputs with  random forest
#' @post /german_credit_rf/predict
#' @serializer html
calculate_prediction <- function(payload, res) {
  tryCatch(
  {
    ## payload should contain "instances", which is a list of vectors of inputs,
    ## test data doesn't need the groud truth for prediction
    ## make sure only the features needed by model for prediction are passed
    ## here colnames(data)[-21] is used so as to map request data to first 20 feature cols
    ## response should be structured as {"payload": { "predictions": [list of predictions] } }
    test_data <- as.data.frame(payload)
    colnames(test_data) <- model.list$artifacts$colsnames[-21]
    # predict and return resula
    pred <- as.numeric(predict(model.list$model, model.list$encoder(test_data, model.list$artifacts)))
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


