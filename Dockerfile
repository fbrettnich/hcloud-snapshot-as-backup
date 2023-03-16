FROM python:alpine3.17 as base

RUN apk --no-cache add tzdata


FROM base as builder

COPY requirements.txt /requirements.txt

RUN pip3 install --prefix=/install -r /requirements.txt


FROM base

ARG USER=hcloud
RUN adduser -D $USER
USER $USER
WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=$USER:$USER snapshot-as-backup.py README.md LICENSE .

ENV IN_DOCKER_CONTAINER=true

CMD [ "python3", "-u", "/app/snapshot-as-backup.py"]
