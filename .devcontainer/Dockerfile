FROM python:3.10

RUN apt-get update && \
    apt-get install build-essential -y &&\
    pip install -U pip

WORKDIR /jupyter-env
RUN python -m venv .
RUN --mount=type=cache,target=/root/.cache \
    bash -c "source bin/activate && pip install jupyterlab ipywidgets"

WORKDIR /project
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt