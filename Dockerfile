############################################################
# Dockerfile to run jamrizzi/volback
# Based on Alpine
############################################################

FROM alpine:3.5

MAINTAINER Jam Risser (jamrizzi)

EXPOSE 8806

ENV PORT=8806
ENV HOST=0.0.0.0
ENV DEBUG=false
ENV DATABASE_DRIVER=sqlite
ENV DATABASE_FILE=api.db
ENV DATABASE_HOST=db
ENV DATABASE_PORT=5432
ENV DATABASE_USER=postgres
ENV DATABASE_PASSWORD=hellodocker

WORKDIR /app/

RUN apk add --no-cache \
        build-base \
        postgresql-dev \
        py-pip \
        python \
        python-dev \
        tini && \
    pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./ /app/

ENTRYPOINT ["/sbin/tini", "--", "python", "server.py"]
