# R Random Forest Example 

## Install Dependencies

Run the below command in R Console to install required R packages

```
install.packages("randomForest")
install.packages("caret")
install.packages('plumber')
```

Running the example:

1. Open R Console with working directory set as `r-models`. Alternatively you can set working directory in R console using `setwd("cortex-certifai-examples/models/r-models")`


2. Run the `train_german_credit.R` script in R Console to train and persist the model to disk 


3. Run the `run_server.R` script in R Console to start the model server on port 8551

Above command starts the webserver on port 8551 using file `predict_german_credit.R`  
 
```
 Running plumber API at http://127.0.0.1:8551
 Running swagger Docs at http://127.0.0.1:8551/__docs__/
 ```

## Predict


**Request**
```
curl --location --request POST '127.0.0.1:8551/german_credit_rf/predict' \
--header 'Content-Type: application/json' \
--data-raw '{
    "payload": {
        "instances": [
            [
                "... < 0 DM",
                6,
                "critical account/ other credits existing (not at this bank)",
                "radio/television",
                1169,
                "unknown/ no savings account",
                ".. >= 7 years",
                4,
                "male : single",
                "others - none",
                4,
                "real estate",
                "> 25 years",
                "none",
                "own",
                2,
                "skilled employee / official",
                1,
                "phone - yes, registered under the customers name",
                "foreign - yes"
            ]
        ]
    }
}'
```

**Response**

```
{"payload":{"predictions":[1]}}
```

## Certifai Scan

`certifai scan -f scanner_definition.yaml`