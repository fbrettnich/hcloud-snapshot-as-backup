FROM python:3.17-alpine as base

RUN apk --no-cache add tzdata


FROM base as builder

COPY requirements.txt /requirements.txt

RUN pip3 install --prefix=/install -r /requirements.txt


FROM base

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

ENV IN_DOCKER_CONTAINER=true

CMD [ "python3", "-u", "/app/snapshot-as-backup.py"]
