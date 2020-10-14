# random_forest_api.R

## This example uses the German Credit dataset originally sourced from
## [Kaggle](https://www.kaggle.com/uciml/german-credit). This is a binaryclassification example.

# Global code; gets executed at plumb() time.

if (!require(jsonlite)) {
  install.packages("jsonlite")
}
# caret is needed for the train/test split; can remove if we aren't doing that.
if (!require(caret)) {
  install.packages("caret")
}
if (!require(randomForest)) {
  install.packages("randomForest")
}

library(jsonlite)
library(caret)
library(randomForest)

data <- read.csv(file = '../german_credit/german_credit_eval.csv', header = TRUE, sep = ',')
set.seed(42)
## here I'm assuming we're generating a dynamic train/test split. For a static split,
## read in train_data using read.csv directly, using the format above.

index <- createDataPartition(data$outcome, p = .8,
                             list = F,
                             times = 1)
outcome_column <- 'outcome'
X <- data[, !(colnames(data) == outcome_column)]
y <- data[outcome_column]
X_train <- X[index,]
X_test <- X[-index,]
y_train <- y[index]
y_test <- y[-index]


num_col <- c(2, 5, 8, 11, 16, 18) # note, R is one-based not zero-based
cat_col <- c(1, 3, 4, 6, 7, 9, 10, 12, 13, 14, 15, 17, 19, 20)

for (cat in cat_col) {
  X_train[[cat]] <- factor(X_train[[cat]], levels = levels(factor(data[[cat]])))
  ## the levels command makes sure we include any levels that aren't in the training set
  ## Will need to edit to read in a pre-defined list of levels, if we aren't dynamically
  ## creating the train/test split
}

defaultValues <- vector(mode = "list", length = 20)
for (num in num_col) {
  X_train[[num]] <- as.numeric(as.character(X_train[[num]])) # will convert any non-numeric to NA, and make sure e.g. "1" gets coded as 1
  defaultValues[[num]] <- mean(X_train[[num]], na.rm = TRUE) # mean imputation for missing values
  X_train[[num]][is.na(X_train[[num]])] <- defaultValues[[num]]
  X_train[[num]] <- scale(X_train[[num]]) # analogous to the standard scalar used in python
}

model <- randomForest(x = X_train, y = as.factor(y_train), ntree = 100, type = 'classification')

## below section creates a web service endpoint and
## invokes function (`calculate_prediction`) to return model predictions when endpoint is invoked

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
    ## payload should contain "instances", which is a list of either vectors of inputs,
    ## or JSONs of inputs obtained using toJSON on a dataframe in R.
    ## test data doesn't need the groud truth for prediction
    ## make sure only the features needed by model for prediction are passed
    ## here colnames(data)[-21] is used so as to map request data to first 20 feature cols
    ## response should be structured as {"payload": { "predictions": [list of predictions] } }
    test_data <- as.data.frame(payload)
    colnames(test_data) <- colnames(data)[-21]

    for (cat in cat_col) {
      test_data[[cat]] <- factor(test_data[[cat]], levels = levels(factor(data[[cat]])))
      ## Will need to edit to read in a pre-defined list of levels, if we aren't dynamically
      ## creating the train/test split
    }

    for (num in num_col) {
      test_data[[num]] <- as.numeric(as.character(test_data[[num]]))
      test_data[[num]][is.na(test_data[[num]])] <- defaultValues[[num]]
      test_data[[num]] <- scale(test_data[[num]],
                                center = attr(X_train[[num]], "scaled:center"),
                                scale = attr(X_train[[num]], "scaled:scale")
      ) # scales using same values as training data
    }

    # predict and return result
    pred <<- as.numeric(predict(model, test_data))
    # create response json { "payload" : {"predictions" : pred} }
    pred_list <<- list(payload = list(predictions = pred))
    pred_json <<- toJSON(pred_list)
    res$status <<- 200
    return(pred_json)
  },
  # handle error and return error message
  # create error response as {"payload":{"error": ["error message"]} }
    error = function(cond) {
      error_list <<- list(payload = list(error = cond))
      error_json <<- toJSON(error_list, force = TRUE)
      res$status <<- 500 # Internal Server errror in predicts
      return(error_json)
    }


  )
}
