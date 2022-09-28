FROM python:3.9-alpine

ENV IN_DOCKER_CONTAINER true
WORKDIR /app
COPY . .

RUN pip3 install -r requirements.txt

CMD [ "python3", "/app/snapshot-as-backup.py"]