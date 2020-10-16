To install the necessary packages (only needed the first time), run

```install.packages('plumber')```

To set up the api, run (e.g.):

1. execute the `train_german_credit.R` script in R Console to train and persist the model to disk 

2. execute the below code snippet in R console to start the model server on port 8551

    ```
    library(plumber)
    pr <- plumber::plumb("predict_german_credit.R")
    pr$run(port=8551)
    ```
   Starts the webserver on port 8551 using file `predict_german_credit.R` 
    ```
    Running plumber API at http://127.0.0.1:8551
    Running swagger Docs at http://127.0.0.1:8551/__docs__/
    ```


## Predict

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
