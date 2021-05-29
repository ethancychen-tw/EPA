FROM python:3.8-alpine

LABEL maintainer="ethan chen"

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev libressl-dev

COPY . /epa

WORKDIR /epa

RUN apk add build-base postgresql-dev libpq --no-cache --virtual .build-deps \
&& pip install --no-cache-dir --upgrade pip \
&& pip3 install -r requirements.txt \
&& pip3 install gunicorn \
&& chmod 755 run_server.sh

EXPOSE 8000

ENTRYPOINT [ "./run_server.sh" ]