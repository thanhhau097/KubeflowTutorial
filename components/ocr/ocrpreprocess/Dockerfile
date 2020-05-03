FROM python:3.7

RUN apt update && apt install -y python3-pip

COPY ./src /pipelines/component/src
RUN pip3 install -r /pipelines/component/src/requirements.txt