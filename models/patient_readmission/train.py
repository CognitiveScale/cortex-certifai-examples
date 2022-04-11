import numpy as np
import pandas as pd
import time, pickle, random
import sys
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score, f1_score
from clean_pipeline import CleanPipeline


def _map_diagnostics(df: pd.DataFrame):
    diag_cols = ['diag_1','diag_2','diag_3']
    for col in diag_cols:
        df[col].replace('?', np.nan, inplace=True)
        df[col].fillna('0', inplace=True)
        # Anything with E or V will get mapped into 'Other' group, so set as '0'
        df.loc[df[col].str.contains('E'), col] = '0'
        df.loc[df[col].str.contains('V'), col] = '0'
        # Any '250.xx' will be mapped to Diabetes
        df.loc[df[col].str.contains('250'), col] = '250'

    df[diag_cols] = df[diag_cols].astype(float)

    # diagnosis grouping
    for col in diag_cols:
        df['temp']='Other'

        condition = (df[col]>=390) & (df[col]<=458) | (df[col]==785)
        df.loc[condition,'temp']='Circulatory'

        condition = (df[col]>=460) & (df[col]<=519) | (df[col]==786)
        df.loc[condition,'temp']='Respiratory'

        condition = (df[col]>=520) & (df[col]<=579) | (df[col]==787)
        df.loc[condition,'temp']='Digestive'

        condition = df[col]==250
        df.loc[condition,'temp']='Diabetes'

        condition = (df[col]>=800) & (df[col]<=999)
        df.loc[condition,'temp']='Injury'

        condition = (df[col]>=710) & (df[col]<=739)
        df.loc[condition,'temp']='Muscoloskeletal'

        condition = (df[col]>=580) & (df[col]<=629) | (df[col]==788)
        df.loc[condition,'temp']='Genitourinary'

        condition = (df[col]>=140) & (df[col]<=239)
        df.loc[condition,'temp']='Neoplasms'

        df.loc[df[col].isnull(),'temp']='Unknown'
        df[col]=df['temp']
        df.drop('temp',axis=1,inplace=True)

    return df


def _convert_to_diagnostic_mapped(dataset_filename: str, converted_filename: str) -> pd.DataFrame:
    df = pd.read_csv(dataset_filename)
    df = _map_diagnostics(df)
    df['readmitted'] = np.where(df['readmitted']!='NO',1,0)
    df.to_csv(converted_filename, index=False)
    return df


def main():
    if len(sys.argv) > 1:
        try:
            explain_size = int(sys.argv[1])
        except ValueError as e:
            print("Optional argument must be an integer to specify the number of explanations to generate")
            sys.exit(1)
    else:
        explain_size = 1000

    random.seed(0)
    np.random.seed(0)

    # Convert and bring in test and training data.
    df = _convert_to_diagnostic_mapped('../../notebooks/datasets/diabetic_data.csv',
                                       'diabetic_data_diagnostic_mapped.csv')

    # Just take the first N rows to explain as the explanation set - we save this here for
    # use by later analysis for the purposes of this example
    df_explain = df[:explain_size]
    df_explain.to_csv('diabetic_data_diagnostic_mapped_explain.csv', index=False)

    y = df['readmitted']
    df.drop('readmitted', axis=1, inplace=True)

    encoder = CleanPipeline()
    encoder.fit(df)

    X = encoder.transform(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

    def scores(name, model, x, y):
        preds = model.predict(x)
        return [
            name,
            accuracy_score(y, preds),
            f1_score(y, preds),
            roc_auc_score(y, model.predict_proba(x)[:,1])
        ]

    model = MLPClassifier(random_state=0, hidden_layer_sizes=(20,20), max_iter=1000)
    model.fit(X_train,y_train)
    results = [scores('mlp', model, X_test, y_test)]

    print(results)

    def save(name, model, encoder=encoder):
        # Package with the encoding as logically part of the black box model.  Done this
        # way to simulate the auto-transformation pipeline you get with auto-ML in deployments
        # like H2O
        encoded_model = Pipeline(steps=[('encoder', encoder), ('model', model)])
        model_obj = {'model': encoded_model, 'encoder': None, 'name': name, 'created': int(time.time())}
        with open(f'readmission_{name}.pkl', 'wb') as file:
            pickle.dump(model_obj, file)
        print(f"Saved: {name}")

    # Save model as pickle file
    save('mlp', model)


if __name__ == "__main__":
    main()
