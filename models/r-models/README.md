To install the necessary packages (only needed the first time), run

```install.packages('plumber')```

To set up the api, run (e.g.):

```
library(plumber)
pr <- plumber::plumb("random_forest_api.R")
pr$run(port=8551)
```
Starts the webserver on port 8551 using file `random_forest_api.R`

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
