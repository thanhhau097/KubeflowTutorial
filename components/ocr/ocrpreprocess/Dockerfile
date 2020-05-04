FROM python:3.7

RUN apt update && apt install -y python3-pip
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=UTF-8 LANG=C.UTF-8 LC_ALL=C.UTF-8

COPY ./src /pipelines/component/src
RUN pip3 install -r /pipelines/component/src/requirements.txt