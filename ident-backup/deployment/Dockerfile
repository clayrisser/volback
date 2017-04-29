############################################################
# Dockerfile to run ident-backup
# Based on Alpine
############################################################

FROM jamrizzi/ident-base:major-refactor

MAINTAINER Jam Risser (jamrizzi)

ENV CONTAINER_ID=""
ENV DATA_TYPE=raw
ENV ENCRYPT=false
ENV KEEP_DAILY=2
ENV KEEP_HOURLY=1
ENV KEEP_MONTHLY=30
ENV KEEP_WEEKLY=14
ENV KEEP_WITHIN=1y
ENV KEEP_YEARLY=200
ENV PASSPHRASE=hellodocker
ENV SERVICE=unknown
ENV STORAGE_ACCESS_KEY=""
ENV STORAGE_SECRET_KEY=""
ENV STORAGE_URL=""

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./ /app/
RUN chmod -R 700 /app/

ENTRYPOINT ["tini", "--", "python", "/app/src/run.py"]
