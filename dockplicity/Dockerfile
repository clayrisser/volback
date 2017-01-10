FROM ubuntu:latest

ENV CRON_SCHEDULE="0 0 0 * * *"
ENV PASSPHRASE=hellodocker
ENV STORAGE_URL=gs://my_google_bucket
ENV COMMAND=cron
ENV SERVICE=""
ENV RESTORE_ALL=false
ENV BLACKLIST=false
ENV ENCRYPT=false
ENV STORAGE_VOLUME=""
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
ENV TIME=now

RUN apt-get update
RUN apt-get install -y python python-pip curl
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin
RUN curl -L https://get.docker.com | bash
RUN curl -L https://github.com/rancher/cli/releases/download/v0.4.1/rancher-linux-amd64-v0.4.1.tar.gz | tar -zxv -C /tmp && mv /tmp/rancher*/* /usr/local/bin
RUN pip install docker && \
    pip install pyyaml && \
    pip install requests
RUN mkdir /docker && \
    touch /docker/cron.log

ADD ./src /docker/src
ADD ./config /docker/config
ADD ./backup.sh /bin/backup
ADD ./restore.sh /bin/restore
RUN chmod -R 700 /docker && \
    chmod +x /bin/backup && \
    chmod +x /bin/restore

CMD bash /docker/run.sh
