FROM python:3.11

RUN apt-get update && \
    apt-get install build-essential -y

WORKDIR /project
COPY requirements.txt .
RUN pip install -r requirements.txt