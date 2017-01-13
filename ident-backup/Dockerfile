FROM ubuntu:latest

ENV PASSPHRASE=hellodocker
ENV STORAGE_ACCESS_KEY=""
ENV STORAGE_SECRET_KEY=""
ENV STORAGE_URL=""
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
RUN curl -L https://get.docker.com | bash
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
