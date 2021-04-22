FROM {{BASE_DOCKER_IMAGE}}

WORKDIR /

RUN apt-get update && \
  apt-get install -y libxml2-dev

COPY ./requirements_bin.txt /tmp/
COPY ./requirements_src.txt /tmp/

#install package available as binaries
RUN cat /tmp/requirements_bin.txt | xargs apt-get install -y -qq

#install non-binary package from source
RUN Rscript /tmp/requirements_src.txt

RUN mkdir /src

COPY src /src
COPY model /model

EXPOSE 8551

CMD ["Rscript", "/src/run_server.R"]

