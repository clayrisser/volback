############################################################
# Dockerfile to build ident-base
# Based on Alpine
############################################################

FROM alpine:3.5

MAINTAINER Jam Risser (jamrizzi)

WORKDIR /app/

RUN apk add --no-cache borgbackup \
    build-base \
    curl \
    docker \
    git \
    make \
    py-pip \
    python \
    tini
