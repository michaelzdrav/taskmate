FROM python:3.8.16-slim-bullseye

# Set the working directory
WORKDIR /run

# Copy requirements.txt and install dependencies
COPY requirements.txt /run/requirements.txt
RUN pip3 install -r /run/requirements.txt

# Copy the Flask application code
COPY web /run/web

# Create a directory for instance files
RUN mkdir /instance

# Copy the templates directory to the correct location
COPY web/Templates /run/web/templates

# Initialise the database
RUN flask --app web init-db

# Set the CMD to run Flask
CMD [ "flask", "--app", "web", "run", "--host", "0.0.0.0", "--port", "5001" ]
