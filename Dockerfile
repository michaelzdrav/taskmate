FROM python:3.8.16-slim-bullseye

# Set the working directory
WORKDIR /run

# Copy requirements.txt and install dependencies
RUN python -m venv venv
COPY requirements.txt ./requirements.txt
RUN venv/bin/pip3 install -r requirements.txt

# Copy required code
COPY web ./web
COPY boot.sh gunicorn.conf.py ./

# Run the application
EXPOSE 5001
RUN chmod a+x boot.sh
ENTRYPOINT ["./boot.sh"]

