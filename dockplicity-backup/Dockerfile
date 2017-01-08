FROM ubuntu:latest

ENV PASSPHRASE=hellodocker
ENV ACCESS_KEY=""
ENV SECRET_KEY=""
ENV TARGET_URL=""
ENV SERVICE=unknown
ENV ENCRYPT=false
ENV DATA_TYPE=raw
ENV CONTAINER_ID=""
ENV KEEP_WITHIN=1y
ENV HOURLY=1
ENV DAILY=2
ENV WEEKLY=14
ENV MONTHLY=30
ENV YEARLY=200

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y automake autotools-dev g++ git libcurl4-gnutls-dev libfuse-dev libssl-dev libxml2-dev make pkg-config python-pip borgbackup
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin
RUN pip install pyyaml && \
    pip install docker
RUN git clone https://github.com/s3fs-fuse/s3fs-fuse.git && \
    cd s3fs-fuse && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install

ADD ./backup.py /scripts/backup.py
ADD ./config /scripts/config
RUN chmod -R 700 /scripts

CMD python /scripts/backup.py
