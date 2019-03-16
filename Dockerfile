# Volback v2.0.0 (https://camptocamp.github.io/volback)
# Copyright (c) 2019 Camptocamp
# Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
# Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

FROM golang:1.11 as builder
WORKDIR /go/src/github.com/codejamninja/volback
COPY . .
RUN make volback

FROM restic/restic:latest as restic

FROM alpine:latest as rclone
RUN wget https://downloads.rclone.org/rclone-current-linux-amd64.zip
RUN unzip rclone-current-linux-amd64.zip
RUN cp rclone-*-linux-amd64/rclone /usr/bin/
RUN chown root:root /usr/bin/rclone
RUN chmod 755 /usr/bin/rclone

FROM debian
RUN apt-get update && \
    apt-get install -y openssh-client && \
	rm -rf /var/lib/apt/lists/*
COPY --from=builder /etc/ssl /etc/ssl
COPY --from=builder /go/src/github.com/codejamninja/volback/volback /bin/
COPY --from=builder /go/src/github.com/codejamninja/volback/providers-config.default.toml /
COPY --from=restic /usr/bin/restic /bin/restic
COPY --from=rclone /usr/bin/rclone /bin/rclone
ENTRYPOINT ["/bin/volback"]
CMD [""]
