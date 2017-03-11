############################################################
# Dockerfile to build ident-base
# Based on Ubuntu
############################################################

FROM ubuntu:latest

MAINTAINER Jam Risser (jamrizzi)

ENV TINI_VERSION v0.14.0

WORKDIR /app/

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /bin/tini
RUN chmod +x /bin/tini

RUN apt-get update && apt-get install -y automake \
    curl \
    autotools-dev \
    borgbackup \
    g++ \
    git \
    libcurl4-gnutls-dev \
    libfuse-dev \
    libssl-dev \
    libxml2-dev \
    make \
    pkg-config \
    python-pip
RUN curl -L https://get.docker.com | bash
RUN pip install pyyaml && \
    pip install docker
RUN git clone https://github.com/s3fs-fuse/s3fs-fuse.git && \
    cd s3fs-fuse && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install
