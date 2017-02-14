############################################################
# Dockerfile to run ident
# Based on Ubuntu
############################################################

FROM ubuntu:16.04

MAINTAINER Jam Risser (jamrizzi)

ENV BLACKLIST=false
ENV CRON_SCHEDULE="0 0 * * *"
ENV DEBUG=false
ENV ENCRYPT=false
ENV KEEP_DAILY=2
ENV KEEP_HOURLY=1
ENV KEEP_MONTHLY=30
ENV KEEP_WEEKLY=14
ENV KEEP_WITHIN=1y
ENV KEEP_YEARLY=200
ENV PASSPHRASE=hellodocker
ENV RANCHER_ACCESS_KEY=""
ENV RANCHER_SECRET_KEY=""
ENV RANCHER_URL=""
ENV RESTORE_ALL=false
ENV SERVICE=""
ENV STORAGE_ACCESS_KEY=""
ENV STORAGE_SECRET_KEY=""
ENV STORAGE_URL=""
ENV TIME=""

RUN apt-get update && apt-get install -y automake \
    autotools-dev \
    g++ \
    git \
    libcurl4-gnutls-dev \
    libfuse-dev libssl-dev \
    libxml2-dev \
    make \
    pkg-config \
    python \
    python-pip \
    curl \
    borgbackup
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin
RUN curl -L https://get.docker.com | bash
RUN curl -L https://github.com/rancher/cli/releases/download/v0.4.1/rancher-linux-amd64-v0.4.1.tar.gz | tar -zxv -C /tmp && mv /tmp/rancher*/* /usr/local/bin
RUN pip install docker && \
    pip install pyyaml && \
    pip install requests
RUN git clone https://github.com/s3fs-fuse/s3fs-fuse.git && \
    cd s3fs-fuse && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install
RUN mkdir /app/ && touch /app/cron.log

ADD ./src /app/src
ADD ./config /app/config
RUN chmod -R 700 /app

ENTRYPOINT ["python", "/app/src/run.py"]
CMD ["cron"]
