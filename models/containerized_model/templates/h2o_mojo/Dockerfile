#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#
FROM {{BASE_DOCKER_IMAGE}}

WORKDIR /

# NOTE: If you are using a base image that does NOT include 'apt', then update the below RUN command to
# use the package management tool available in the container to install any latest security updates.
RUN apt update && apt upgrade -y

RUN pip install --no-cache-dir datatable==0.11.0 && \
    pip install --no-binary=protobuf protobuf==3.13.0

COPY ext_packages /tmp/ext_packages
COPY packages/all/cortex-certifai-common*.zip /tmp/
COPY packages/all/cortex-certifai-model-sdk*.zip /tmp/
COPY requirements.txt /tmp/

RUN pip install --no-cache-dir \
     $(find /tmp -name cortex-certifai-common-*.zip)[s3,gcp,azure] \
     $(find /tmp -name cortex-certifai-model*.zip) \
     $(find /tmp/ext_packages -name *.whl)

RUN pip install -r /tmp/requirements.txt

COPY src /src
COPY model /model
COPY license /license

EXPOSE 8551

ENTRYPOINT ["python", "src/prediction_service.py"]
