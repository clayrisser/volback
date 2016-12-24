FROM ubuntu:latest

ENV PASSPHRASE=hellodocker
ENV TARGET_URL=gs://my_google_bucket
ENV BACKUP_DIR=/volumes
ENV ALLOW_SOURCE_MISMATCH=true
ENV RESTORE_TIME=now
ENV RESTORE_VOLUME=""
ENV FORCE=false

RUN apt-get update
RUN apt-get install -y duplicity python-pip gsutil libwww-perl curl
RUN pip install boto
RUN pip install dropbox
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin

VOLUME /volumes

ADD ./restore.py /scripts/restore.py
RUN chmod -R 700 /scripts

CMD python /scripts/restore.py
