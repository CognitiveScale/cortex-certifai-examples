import pandas as pd
from sklearn.model_selection import train_test_split
import os

ROOT_DIR = "../"
RANDOM_SEED = 0
TEST_SIZE = 0.3
EXPLANATION_MAX_SIZE = 100

IGNORE_PREVIOUS_SPLITS = ["train.csv", "test.csv", "eval.csv", "expln.csv"]
IGNORE_AD_HOC = ["german_credit.csv"]
IGNORE_ENDSWITH = IGNORE_PREVIOUS_SPLITS + IGNORE_AD_HOC


def find_dataset(dr, root="."):
    l = []
    for path, dirs, files in os.walk(root):
        if dr in dirs:
            for _, _, fs in os.walk(os.path.join(path, dr)):
                l.extend(os.path.join(path, dr, fl) for fl in fs)
    return list(filter(lambda x: not any([x.endswith(z) for z in IGNORE_ENDSWITH]), l))


def split_dataset():
    datasets_to_split = find_dataset("data", ROOT_DIR)
    for ds in datasets_to_split:
        df = pd.read_csv(ds)
        train, test = train_test_split(
            df, test_size=TEST_SIZE, random_state=RANDOM_SEED
        )

        train_ds, test_ds, eval_ds, expln_ds = map(
            lambda x: ds.replace(".csv", x),
            map(lambda x: ("-" + x), IGNORE_PREVIOUS_SPLITS),
        )
        # evaluation dataset for certifai is assumed to be  union of train and test dataset(i.e original df)
        # explanation dataset for certifai is sampled from test dataset (maxsize=100)

        write_to_csv(
            [(train, train_ds), (test, test_ds), (df, eval_ds), (test.sample(n=EXPLANATION_MAX_SIZE, random_state=RANDOM_SEED), expln_ds)]
        )


def write_to_csv(ws):
    for (df, ds) in ws:
        print(f"Saving {ds} ")
        df.to_csv(ds, index=False)


if __name__ == "__main__":
    split_dataset()

