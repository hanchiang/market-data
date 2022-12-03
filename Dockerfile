# Dockerfile

# pull the official docker image
FROM python:3.9.8-slim as base

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt update && apt install -y build-essential curl git
COPY requirements.txt .
RUN pip install -r requirements.txt


# ssh
RUN mkdir -p /root/.ssh
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

RUN pip install git+ssh://git@github.com/hanchiang/barchart_api.git@0.1.2 && rm /root/.ssh/id_rsa

# copy project
COPY . .

FROM base as dev
CMD ["uvicorn", "--reload", "--app-dir", "src/server", "main:app"]