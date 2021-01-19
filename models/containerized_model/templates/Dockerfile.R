FROM {{BASE_DOCKER_IMAGE}}

WORKDIR /

RUN apt-get update && \
  apt-get install -y libxml2-dev

COPY ./requirements_bin_R.txt /tmp/
COPY ./requirements_src_R.txt /tmp/

#install package available as binaries
RUN cat /tmp/requirements_bin_R.txt | xargs apt-get install -y -qq

#install non-binary package from source
RUN Rscript /tmp/requirements_src_R.txt

RUN mkdir /src

COPY src /src
COPY model /model

EXPOSE 8551

CMD ["Rscript", "/src/run_server.R"]

