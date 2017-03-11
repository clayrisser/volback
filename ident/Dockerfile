############################################################
# Dockerfile to run ident
# Based on Ubuntu
############################################################

FROM jamrizzi/ident-base:latest

MAINTAINER Jam Risser (jamrizzi)

ENV BLACKLIST=false
ENV CRON_SCHEDULE="0 0 * * *"
ENV DEBUG=false
ENV ENCRYPT=false
ENV KEEP_DAILY=2
ENV KEEP_HOURLY=1
ENV KEEP_MONTHLY=30
ENV KEEP_WEEKLY=14
ENV KEEP_WITHIN=1y
ENV KEEP_YEARLY=200
ENV PASSPHRASE=hellodocker
ENV RANCHER_ACCESS_KEY=""
ENV RANCHER_SECRET_KEY=""
ENV RANCHER_URL=""
ENV RESTORE_ALL=false
ENV SERVICE=""
ENV STORAGE_ACCESS_KEY=""
ENV STORAGE_SECRET_KEY=""
ENV STORAGE_URL=""
ENV TIME=""

RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz | tar -x -C /usr/local/bin && \
    curl -L https://github.com/rancher/cli/releases/download/v0.4.1/rancher-linux-amd64-v0.4.1.tar.gz | tar -zxv -C /tmp && mv /tmp/rancher*/* /usr/local/bin && \
    pip install requests

RUN touch /app/cron.log

ADD ./src /app/src
ADD ./config /app/config
RUN chmod -R 700 /app

ENTRYPOINT ["tini", "--", "python", "/app/src/run.py"]
CMD ["cron"]
