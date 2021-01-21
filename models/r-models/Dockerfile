FROM rocker/r-apt:bionic

WORKDIR /

RUN apt-get update && \
  apt-get install -y libxml2-dev

COPY ./requirements-bin.txt /tmp/
COPY ./requirements-src.R /tmp/

#install package available as binaries
RUN cat /tmp/requirements-bin.txt | xargs apt-get install -y -qq

#install non-binary package from source
RUN Rscript /tmp/requirements-src.R

RUN mkdir /src

COPY *.rds /src
COPY *.R /src/

EXPOSE 8551

CMD ["Rscript", "/src/run_server.R"]

