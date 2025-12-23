FROM python:3.14-alpine

RUN apk --no-cache add tzdata

WORKDIR /app

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "10001" \
    app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER app

COPY snapshot-as-backup.py README.md LICENSE ./

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV IN_DOCKER_CONTAINER=true

CMD [ "python3", "-u", "/app/snapshot-as-backup.py"]
