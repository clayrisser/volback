FROM ubuntu:latest

ENV CRON_SCHEDULE="0 0 0 * * *"
ENV PASSPHRASE=hellodocker
ENV BACKUP_TYPE=incr
ENV TARGET_URL=gs://my_google_bucket
ENV REMOVE_ALL_BUT_N_FULL=12
ENV REMOVE_ALL_INC_BUT_OF_N_FULL=144
ENV REMOVE_OLDER_THAN=6M
ENV FULL_IF_OLDER_THAN=2W
ENV ALLOW_SOURCE_MISMATCH=true
ENV COMMAND=cron
ENV SERVICE=""
ENV RESTORE_ALL=false
ENV BLACKLIST=false

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

ADD ./run.sh /docker/run.sh
ADD ./src /docker/src
ADD ./config /docker/config
RUN chmod -R 700 /docker

CMD bash /docker/run.sh
