FROM python:3.7

RUN apt update && apt install -y python3-pip

RUN set -ex && pip3 install -r ./src/requirements.txt

COPY ./src /pipelines/component/src