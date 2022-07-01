FROM python:3.8-slim-buster
WORKDIR /server
RUN apt-get update
RUN apt-get -y install build-essential
RUN apt-get -y install default-libmysqlclient-dev
RUN apt-get -y install nano
COPY requirements.txt requirements.txt
RUN pip install -r requirements
COPY . .
CMD ["python", "-m", "flask", "run", "--host:0.0.0.0"]