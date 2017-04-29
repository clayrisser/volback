############################################################
# Dockerfile to run ident-restore
# Based on Alpine
############################################################

FROM jamrizzi/ident-base:major-refactor

MAINTAINER Jam Risser (jamrizzi)

ENV CONTAINER_ID=""
ENV DATA_TYPE=raw
ENV ENCRYPT=false
ENV PASSPHRASE=hellodocker
ENV SERVICE=unknown
ENV STORAGE_ACCESS_KEY=""
ENV STORAGE_SECRET_KEY=""
ENV STORAGE_URL=""
ENV TIME=9999999999

WORKDIR /app/

ADD ./src/ /app/src/
ADD ./config/ /app/config/
RUN chmod -R 700 /app/

ENTRYPOINT ["tini", "--", "python", "/app/src/run.py"]
