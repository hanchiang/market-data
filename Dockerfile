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

# set up ssh, install barchart api
RUN mkdir -p /root/.ssh
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY secret/id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

ARG BARCHART_API_TAG
RUN if [ -z "$BARCHART_API_TAG" ]; then echo "BARCHART_API_TAG is required"; exit 1; fi
RUN pip install git+ssh://git@github.com/hanchiang/barchart_api.git@$BARCHART_API_TAG && rm /root/.ssh/id_rsa

COPY . .
RUN rm -rf "$(pwd)/secret"
ENV PYTHONPATH "${PYTHONPATH}:$(pwd)"

FROM base as dev
CMD ["uvicorn", "--reload", "--app-dir", "src/server", "main:app"]