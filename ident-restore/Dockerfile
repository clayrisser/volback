FROM ubuntu:latest

ENV PASSPHRASE=hellodocker
ENV STORAGE_ACCESS_KEY=""
ENV STORAGE_SECRET_KEY=""
ENV STORAGE_URL=""
ENV SERVICE=unknown
ENV ENCRYPT=false
ENV DATA_TYPE=raw
ENV CONTAINER_ID=""
ENV TIME=""

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
RUN locale-gen en_US.UTF-8

ADD ./restore.py /scripts/restore.py
ADD ./config /scripts/config
RUN chmod -R 700 /scripts

CMD python /scripts/restore.py
