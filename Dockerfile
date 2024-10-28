FROM python:3.12.2-alpine3.19

ENV PYTHONUNBUFFERED 1
ENV RUNNING_IN_DOCKER True

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
