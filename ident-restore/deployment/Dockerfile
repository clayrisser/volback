############################################################
# Dockerfile to run ident-restore
# Based on Ubuntu
############################################################

FROM jamrizzi/ident-base:latest

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

MAINTAINER Jam Risser (jamrizzi)

RUN locale-gen en_US.UTF-8

ADD ./src/ /app/src/
ADD ./config/ /app/config/
RUN chmod -R 700 /app/

ENTRYPOINT ["tini", "--"]
CMD ["node", "server.js"]
