FROM python:3.7-slim
LABEL key="ChainBreaker"

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get -y install build-essential 
RUN apt-get -y install default-libmysqlclient-dev
RUN apt-get -y install nano
RUN mkdir /ibm
WORKDIR /ibm
COPY ./app /ibm
RUN pip install -r ./requirements.txt