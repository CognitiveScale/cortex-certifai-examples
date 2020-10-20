# Sample base image, needs to be replaced by the specific model env image
FROM continuumio/miniconda3:4.7.10

WORKDIR /app

COPY prediction_service.py prediction_service.py
COPY packages/cortex-certifai*.zip /tmp/

RUN pip install --no-cache-dir \
     $(find /tmp -name cortex-certifai-common-*.zip)[s3] \
     $(find /tmp -name cortex-certifai-model*.zip)

EXPOSE 8551

ENTRYPOINT ["python", "prediction_service.py"]
