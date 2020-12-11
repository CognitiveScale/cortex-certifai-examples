"
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"
# train_german_credit.R

## This example uses the German Credit dataset originally sourced from
## [Kaggle](https://www.kaggle.com/uciml/german-credit). This is a binaryclassification example.

# caret is needed for the train/test split;

if (!require(caret)) {
  install.packages("caret")
}
if (!require(randomForest)) {
  install.packages("randomForest")
}

library(caret)
library(randomForest)

set.seed(42)

data <- read.csv(file = '../german_credit/german_credit_eval.csv', header = TRUE, sep = ',')

## assuming we're generating a dynamic train/test split. For a static split,
## read in train_data using read.csv directly, using the format above.
index <- createDataPartition(data$outcome, p = .8,
                             list = F,
                             times = 1)
outcome_column <- 'outcome'
cols <- colnames(data)[-21]

X <- data[, cols]
y <- data[outcome_column]
X_train <- X[index,]
X_test <- X[-index,]
y_train <- y[index]
y_test <- y[-index]

num_col <- c(2, 5, 8, 11, 16, 18) # note, R is one-based not zero-based
cat_col <- c(1, 3, 4, 6, 7, 9, 10, 12, 13, 14, 15, 17, 19, 20)

#store levels of factor features
levels_all <- list()
for (cat in cat_col) {
  z <- levels(factor(data[[cat]]))
  levels_all[[cat]] <- z
}

for (cat in cat_col) {
  X_train[[cat]] <- factor(X_train[[cat]], levels = levels_all[[cat]])
  ## the levels command makes sure we include any levels that aren't in the training set
}

defaultValues <- vector(mode = "list", length = 20)
encoder <- vector(mode = 'list')

for (num in num_col) {
  X_train[[num]] <- as.numeric(as.character(X_train[[num]])) # will convert any non-numeric to NA, and make sure e.g. "1" gets coded as 1
  defaultValues[[num]] <- mean(X_train[[num]], na.rm = TRUE) # mean imputation for missing values
  X_train[[num]][is.na(X_train[[num]])] <- defaultValues[[num]]
  X_train[[num]] <- scale(X_train[[num]]) # analogous to the standard scalar used in python
  encoder$center[num] <- attr(X_train[[num]], "scaled:center")  #persist scale$center for predict pipeline
  encoder$scale[num] <- attr(X_train[[num]], "scaled:scale")    #persist scaled$scale for predict pipeline
}

#model train
model <- randomForest(x = X_train, y = as.factor(y_train), ntree = 190, type = 'classification')

#encoder pipeline: for applying same encodings to new raw data
encoder_pipeline <- function(df, artifacts) {
  num_col <- artifacts$num_col
  cat_col <- artifacts$cat_col
  level_store <- artifacts$level_store
  defaultValues <- artifacts$defaultValues
  encoder <- artifacts$encoder

  for (cat in cat_col) {
    df[[cat]] <- factor(df[[cat]], levels = level_store[[cat]])
  }
  for (num in num_col) {
    df[[num]] <- as.numeric(as.character(df[[num]]))
    df[[num]][is.na(df[[num]])] <- defaultValues[[num]]
    df[[num]] <- scale(df[[num]], center = encoder$center[num], scale = encoder$scale[num])
    # scales using same values as training data
  }

  return(df)

}

#save artifacts
artifacts <- vector(mode = 'list')
artifacts$num_col <- num_col
artifacts$cat_col <- cat_col
artifacts$colsnames <- colnames(data)
artifacts$encoder <- encoder
artifacts$level_store <- levels_all
artifacts$defaultValues <- defaultValues


#persist model and encoder_pipeline to disk
model.list <- vector(mode = 'list')
model.list$encoder <- encoder_pipeline
model.list$artifacts <- artifacts
model.list$model <- model

file_name <- "german_credit_rf.rds"
paste("saving model and artifacts to disk as", file_name)
saveRDS(object = model.list, file = file_name)
