#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#
FROM {{BASE_DOCKER_IMAGE_NAME}}:{{BASE_DOCKER_IMAGE_TAG}}

WORKDIR /app

COPY prediction_service.py prediction_service.py
COPY packages/cortex-certifai*.zip /tmp/

RUN pip install --no-cache-dir \
     $(find /tmp -name cortex-certifai-common-*.zip)[s3] \
     $(find /tmp -name cortex-certifai-model*.zip)

EXPOSE 8551

ENTRYPOINT ["python", "prediction_service.py"]
