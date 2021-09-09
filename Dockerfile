FROM python:3.9.6

WORKDIR /app
COPY ./app .

RUN apt-get update -y
RUN apt-get install -y gunicorn

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
