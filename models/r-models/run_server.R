if (!require(caret)) {
  install.packages("plumber")
}

library(plumber)
pr <- plumber::plumb("predict_german_credit.R")
pr$run(port=8551)