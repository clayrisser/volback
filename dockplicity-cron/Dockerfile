FROM ubuntu:latest

ENV CRON_SCHEDULE="0 0 0 * * *"
ENV VOLUME_DRIVER="local"
ENV PASSPHRASE=hellodocker
ENV BACKUP_TYPE=incr
ENV TARGET_URL=gs://my_google_bucket
ENV REMOVE_ALL_BUT_N_FULL=12
ENV REMOVE_ALL_INC_BUT_OF_N_FULL=144
ENV REMOVE_OLDER_THAN=6M
ENV FULL_IF_OLDER_THAN=2W
ENV ALLOW_SOURCE_MISMATCH=true

RUN apt-get update
RUN apt-get install -y python python-pip curl
RUN pip install docker
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin

ADD ./cron.py /scripts/cron.py
RUN chmod -R 700 /scripts

CMD touch /var/log/cron.log \
    go-cron "$CRON_SCHEDULE" python /scripts/cron.py >> /var/log/cron.log \
    tail -f /var/log/cron.log
