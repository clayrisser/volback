FROM ubuntu:latest

ENV PASSPHRASE=hellodocker
ENV BACKUP_TYPE=incr
ENV TARGET_URL=gs://my_google_bucket
ENV BACKUP_DIR=/volumes
ENV CRON_SCHEDULE="0 0 0 * * *"
ENV FULL_MAX_COUNT=12
ENV INCR_MAX_COUNT=144
ENV MAX_TIME=6M
ENV RESTORE_TIME=now
ENV FULL_IF_OLDER_THAN=2W
ENV ALLOW_SOURCE_MISMATCH=false

RUN apt-get update
RUN apt-get install -y duplicity python-pip gsutil libwww-perl curl
RUN pip install boto
RUN pip install dropbox
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin

VOLUME /volumes

ADD ./scripts /scripts
RUN chmod -R 700 /scripts

CMD bash /scripts/run.sh
