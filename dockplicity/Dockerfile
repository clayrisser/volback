FROM ubuntu:latest

ENV CRON_SCHEDULE="0 0 0 * * *"
ENV PASSPHRASE=hellodocker
ENV STORAGE_URL=""
ENV SERVICE=""
ENV RESTORE_ALL=false
ENV BLACKLIST=false
ENV ENCRYPT=false
ENV STORAGE_ACCESS_KEY=""
ENV STORAGE_SECRET_KEY=""
ENV KEEP_WITHIN=1y
ENV HOURLY=1
ENV DAILY=2
ENV WEEKLY=14
ENV MONTHLY=30
ENV YEARLY=200
ENV RANCHER_URL=""
ENV RANCHER_ACCESS_KEY=""
ENV RANCHER_SECRET_KEY=""
ENV TIME=""

RUN apt-get update
RUN apt-get install -y automake autotools-dev g++ git libcurl4-gnutls-dev libfuse-dev libssl-dev libxml2-dev make pkg-config python python-pip curl borgbackup
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin
RUN curl -L https://get.docker.com | bash
RUN curl -L https://github.com/rancher/cli/releases/download/v0.4.1/rancher-linux-amd64-v0.4.1.tar.gz | tar -zxv -C /tmp && mv /tmp/rancher*/* /usr/local/bin
RUN pip install docker && \
    pip install pyyaml && \
    pip install requests
RUN mkdir /docker && \
    touch /docker/cron.log
RUN git clone https://github.com/s3fs-fuse/s3fs-fuse.git && \
    cd s3fs-fuse && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install

ADD ./src /docker/src
ADD ./config /docker/config
ADD ./backup.sh /bin/backup
ADD ./restore.sh /bin/restore
RUN chmod -R 700 /docker && \
    chmod +x /bin/backup && \
    chmod +x /bin/restore

CMD go-cron "$CRON_SCHEDULE" python /docker/src/backup.py >> /docker/cron.log
