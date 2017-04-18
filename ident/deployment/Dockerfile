############################################################
# Dockerfile to run Realtytopia Back-end
# Based on Alpine
############################################################

FROM alpine:3.5

MAINTAINER Jam Risser (jamrizzi)

EXPOSE 8000

ENV SECRET_KEY=hellodocker
ENV DEBUG=false
ENV ALLOWED_HOSTS="*"

WORKDIR /app/

RUN apk add --no-cache build-base \
    git \
    nginx \
    py-pip \
    python \
    supervisor \
    tini \
    uwsgi-python
RUN pip install --upgrade pip && \
    mkdir -p /run/nginx

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./deployment/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./deployment/supervisord.conf /etc/supervisord.conf
COPY ./ /app/
RUN chown -R nobody:nobody /app/ && \
    python manage.py collectstatic --noinput && \
    python manage.py makemigrations && \
    python manage.py migrate

ENTRYPOINT ["/sbin/tini", "--", "/usr/bin/supervisord", "-n"]
