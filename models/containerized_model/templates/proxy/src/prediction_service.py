"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import json
import os
from typing import Optional

import requests
from certifai.model.sdk import SimpleModelWrapper
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import numpy as np


class Proxy(SimpleModelWrapper):
    """
    Certifai Proxy Wrapper to a hosted model webservice
    Proxy class acts as a proxy service between any hosted model webservice and Certifai.

    Subclass's Certifai `SimpleModelWrapper` to start a http webservice by default at '0.0.0.0:8551/predict' which
    - receives prediction POST request from Certifai,
    - transforms (`transform_request_to_hosted_model_schema`) to hosted model service endpoint schema,
    - invokes ('predict`) the hosted model service endpoint (`hosted_model_url`) with the correct json schema,
    - transforms (`transform_response_to_certifai_predict_schema`) received response from above to Certifai `predict` schema
    - returns the formatted response to Certifai
    """

    def __init__(self,
                 hosted_model_url: str,
                 host: Optional[str] = '0.0.0.0',
                 port: Optional[int] = 8551,
                 endpoint_url: Optional[str] = '/predict',
                 **optional_args):
        """
        :param Optional[str] host: hostname proxy class service listens on, defaults to `0.0.0.0`
        :param Optional[int] port: port proxy class service listens on, defaults to `8551`
        :param Optional[str] endpoint_url: endpoint url for the proxy class service. defaults to `/predict`
        :param str hosted_model_url: hosted model webservice url to invoke using http/s /POST
        :param Optional[dict] optional_args: python dict holding any additional configuration (key/value) that maybe be required for
            - model webservice url invoke like service http headers (may have auth tokens), or
            - request/response transformation like column names etc.
        """
        self._create_session()
        self.hosted_model_url = hosted_model_url
        self.optional_args = optional_args
        SimpleModelWrapper.__init__(self,
                                    endpoint_url=endpoint_url,
                                    host=host,
                                    port=int(port))

    def _create_session(self) -> None:
        """Creates requests session object to hold http/https connections

        :rtype: None
        """
        self._session = requests.Session()
        max_retries = Retry(
            total=5,
            backoff_factor=0.2,
            status_forcelist=[500, 502, 503, 504],
            method_whitelist=frozenset(['GET', 'POST']),
            raise_on_status=False)

        self._session.mount('http://', HTTPAdapter(max_retries=max_retries))
        self._session.mount('https://', HTTPAdapter(max_retries=max_retries))

    @staticmethod
    def transform_request_to_hosted_model_schema(instances: np.ndarray, **kwargs) -> json:
        """Transforms incoming Certifai request to hosted model json schema. Returns json formatted string.
        Update this method to transform data `instances` (np. ndarrays) to hosted model service expected schema.
        Transformed data is further used to make /POST requests inside the `predict` method

        :param np.ndarray instances: numpy array of shape (n_samples, n_features) to predict on
        :param Optional[dict] kwargs: optional python dict, can be used for transformation
        :rtype: str
        """
        # sample transformation for reference (uses certifai model server request schema for illustration)
        # {
        #     "payload": {
        #         "instances": [[]]
        #     }
        # }
        json_instances = {
            "payload": {
                "instances": instances.tolist()
            }
        }
        return json.dumps(json_instances)

    @staticmethod
    def transform_response_to_certifai_predict_schema(data: dict, **kwargs) -> np.ndarray:
        """Transforms hosted model service invoke /POST response dict to np.ndarrays. Returns np.ndarray
        Update this method to transform response dict to extract and convert model predictions to
        return numpy array of shape (n_samples,)

        :param dict data: response dict containing model predictions.
        :param Optional[dict] kwargs: optional python dict, can used for transformation.
        :rtype np.ndarray
        """

        # sample transformation for reference (uses certifai model server response schema for illustration)
        # {
        #     "payload": {
        #         "predictions": []
        #     }
        # }
        #
        #
        return np.array(data['payload']['predictions'])

    def predict(self, npinstances) -> np.ndarray:
        """Certifai SimpleModelWrapper.predict (overridden method). Invokes the hosted model service using http/s /POST

        :param np.ndarray npinstances: numpy array of shape (n_samples, n_features) to predict on
        :return: numpy array of model predictions of shape (n_samples,)
        :rtype: np.ndarray
        """
        kwargs = {}
        transformed_request = self.transform_request_to_hosted_model_schema(npinstances, **self.optional_args)
        resp = self._session.post(
            self.hosted_model_url,
            data=transformed_request,
            headers=self.optional_args.get('headers'),
            **kwargs
        )
        resp_json = json.loads(resp.text)
        return self.transform_response_to_certifai_predict_schema(resp_json, **self.optional_args)


if __name__ == "__main__":
    # add any additional headers that maybe required in `opt_args.headers`.
    # if secret/auth token needs to be passed as environment variable take a look at
    # `Authorization` sample example as shown in the `opt_args.headers.Authorization`
    # make sure to add any environment variable used here to
    # `environment.yml` file for the purpose of containerization/deployment

    opt_args = {
        'headers': {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        'columns': []
    }

    # optional model auth header bearer token
    hosted_model_auth_header = f'Bearer {os.getenv("HOSTED_MODEL_AUTH_HEADER_TOKEN")}' if os.getenv(
        'HOSTED_MODEL_AUTH_HEADER_TOKEN') else None
    if hosted_model_auth_header:
        opt_args['headers']['Authorization'] = hosted_model_auth_header

    # hosted model url
    default_hosted_model_url = ''
    hosted_model_url = os.getenv('HOSTED_MODEL_URL') if os.getenv(
        'HOSTED_MODEL_URL') else default_hosted_model_url
    if not hosted_model_url:
        raise ValueError('either `HOSTED_MODEL_URL` env variable is not set or `default_hosted_model_url` is empty')

    app = Proxy(hosted_model_url=hosted_model_url,
                host="0.0.0.0",
                **opt_args)
    app.run(log_level='Warning')
