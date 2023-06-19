FROM python:3.8.16-slim-bullseye

# Pass db environment variable
ARG DATABASE_HOST
ENV DATABASE_HOST=${DATABASE_HOST}

ARG DATABASE_PORT
ENV DATABASE_PORT=${DATABASE_PORT}

# Set the working directory
WORKDIR /run

RUN apt-get update \
    && apt-get install -y \
    build-essential \
    netcat

# Copy requirements.txt and install dependencies
RUN python -m venv venv
COPY requirements.txt ./requirements.txt
RUN venv/bin/pip3 install -r requirements.txt

# Copy required code
EXPOSE 5001
COPY migrations ./migrations
COPY boot.sh gunicorn.conf.py ./
RUN chmod a+x boot.sh
COPY web ./web

# Run the application
ENTRYPOINT ["./boot.sh"]