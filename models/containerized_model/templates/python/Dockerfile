#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#
FROM {{BASE_DOCKER_IMAGE}}

WORKDIR /

COPY packages/all/cortex-certifai-common*.zip /tmp/
COPY packages/all/cortex-certifai-model-sdk*.zip /tmp/
COPY requirements.txt /tmp/

RUN pip install --no-cache-dir \
     $(find /tmp -name cortex-certifai-common-*.zip)[s3] \
     $(find /tmp -name cortex-certifai-model*.zip)

# To enable using gcp / azure cloud storage, uncomment the following lines
#RUN pip install --no-cache-dir \
#     $(find /tmp -name cortex-certifai-common-*.zip)[gcp] \
#     $(find /tmp -name cortex-certifai-common-*.zip)[azure]

RUN pip install -r /tmp/requirements.txt

COPY src /src
COPY model /model

EXPOSE 8551

ENTRYPOINT ["python", "src/prediction_service.py"]
