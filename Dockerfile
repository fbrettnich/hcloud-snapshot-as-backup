FROM python:3.9-alpine

ENV IN_DOCKER_CONTAINER true
ENV EXTERNAL_CRON false
WORKDIR /app
COPY . .

RUN pip3 install -r requirements.txt

CMD [ "python3", "-u", "/app/snapshot-as-backup.py"]
