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

# set up ssh, install market data library
RUN mkdir -p /root/.ssh
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY secret/id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

ARG MARKET_DATA_LIBRARY_TAG
RUN if [ -z "$MARKET_DATA_LIBRARY_TAG" ]; then echo "MARKET_DATA_LIBRARY_TAG is required"; exit 1; fi
RUN pip install git+ssh://git@github.com/hanchiang/market_data_api.git@$MARKET_DATA_LIBRARY_TAG && rm /root/.ssh/id_rsa

COPY . .
RUN rm -rf "$(pwd)/secret"
ENV PYTHONPATH "${PYTHONPATH}:$(pwd)"

FROM base as dev
CMD ["uvicorn", "--reload", "--app-dir", "src/server", "main:app"]
