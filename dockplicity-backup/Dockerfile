FROM ubuntu:latest

ENV PASSPHRASE=hellodocker
ENV BACKUP_TYPE=incr
ENV TARGET_URL=gs://my_google_bucket
ENV BACKUP_DIR=/volumes
ENV REMOVE_ALL_BUT_N_FULL=12
ENV REMOVE_ALL_INC_BUT_OF_N_FULL=144
ENV REMOVE_OLDER_THAN=6M
ENV FULL_IF_OLDER_THAN=2W
ENV ALLOW_SOURCE_MISMATCH=true

RUN apt-get update
RUN apt-get install -y duplicity python-pip gsutil libwww-perl curl
RUN pip install boto
RUN pip install dropbox
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin

VOLUME /volumes

ADD ./backup.py /scripts/backup.py
RUN chmod -R 700 /scripts

CMD python /scripts/backup.py
