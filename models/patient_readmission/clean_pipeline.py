from typing import Union

import numpy as np
import pandas as pd
from certifai.common.utils.encoding import CatEncoder


class CleanPipeline:
    def __init__(self):
        self._cat_encoder = None
        self._invariate_cols = None
        self._columns = None

    def _clean(self, df: pd.DataFrame):
        df.replace('?', np.nan, inplace=True)
        # IDs and known low-info columns
        df.drop(['weight','medical_specialty','payer_code', 'encounter_id','patient_nbr','admission_type_id',
                 'discharge_disposition_id','admission_source_id'], axis=1, inplace=True)

        # dropping columns with no variation
        df.drop(columns=self._invariate_cols, inplace=True)

        def parse_age(r):
            f, to = r[1:-1].split('-')
            return int((int(to) + int(f))/2)

        df['age'] = df['age'].map(parse_age)

        return df

    def fit(self, df: pd.DataFrame):
        self._columns = list(df.columns)
        self._invariate_cols = [c for c in df.columns if len(df[c].unique()) < 2]
        df = df.copy()
        self._clean(df)
        self._cat_encoder = CatEncoder(cat_columns=df.select_dtypes('object').columns, normalize=False)
        self._cat_encoder.fit(df)

    def transform(self, data: Union[pd.DataFrame, np.ndarray]):
        if self._cat_encoder is None:
            raise ValueError("Cleaning pipeline has not been fit")

        if isinstance(data, np.ndarray):
            df = pd.DataFrame(data, columns=self._columns)
        else:
            df = data.copy()
        self._clean(df)
        return self._cat_encoder.transform(df)
