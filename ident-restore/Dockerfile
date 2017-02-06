############################################################
# Dockerfile to run ident restore
# Based on Ubuntu
############################################################

FROM ubuntu:16.04

MAINTAINER Jam Risser (jamrizzi)

ENV CONTAINER_ID=""
ENV DATA_TYPE=raw
ENV ENCRYPT=false
ENV PASSPHRASE=hellodocker
ENV SERVICE=unknown
ENV STORAGE_ACCESS_KEY=""
ENV STORAGE_SECRET_KEY=""
ENV STORAGE_URL=""
ENV TIME=9999999999

WORKDIR /app

RUN apt-get update && apt-get install -y curl \
    automake \
    autotools-dev \
    g++ \
    git \
    libcurl4-gnutls-dev \
    libfuse-dev \
    libssl-dev \
    libxml2-dev \
    make \
    pkg-config \
    python-pip \
    borgbackup
RUN curl -L https://get.docker.com | bash
RUN pip install pyyaml && \
    pip install docker
RUN git clone https://github.com/s3fs-fuse/s3fs-fuse.git && \
    cd s3fs-fuse && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install
RUN locale-gen en_US.UTF-8

ADD ./src /app/src
ADD ./config /app/config
RUN chmod -R 700 /app

ENTRYPOINT ["python", "/app/src/run.py"]
