FROM {{BASE_DOCKER_IMAGE}}

WORKDIR /

# NOTE: If you are using a base image that does NOT include 'apt', then update the below RUN command to
# use the package management tool available in the container to install any latest security updates.
RUN apt update && apt upgrade && \
  apt install -y libxml2-dev

COPY ./requirements_bin.txt /tmp/
COPY ./requirements_src.txt /tmp/

#install package available as binaries
RUN cat /tmp/requirements_bin.txt | xargs apt install -y -qq

#install non-binary package from source
RUN Rscript /tmp/requirements_src.txt

RUN mkdir /src

COPY src /src
COPY model /model

EXPOSE 8551

CMD ["Rscript", "/src/run_server.R"]

