BUILD_TIME := $(shell date +%FT%T%z)
PROJECT    := $(shell basename $(PWD))

env: 
	@if [ ! -f .env ]; then \
        secret_key=$$(echo $$RANDOM | base64); \
        echo "SECRET_KEY=$$secret_key" >> .env; \
		echo "MAIL_SERVER=smtp.googlemail.com" >> .env; \
		echo "MAIL_PORT=587" >> .env; \
		echo "MAIL_USE_TLS=1" >> .env; \
		echo "MAIL_USERNAME=admin" >> .env; \
		echo "MAIL_PASSWORD=password" >> .env; \
		echo "SMTP_ENABLED=False" >> .env; \
		echo "SQLALCHEMY_DATABASE_URI=postgresql://username:password@host:port/taskmate"; \
		echo "DATABASE_HOST=postgresql"; \
		echo "DATABASE_PORT=5432"; \
		echo "CELERY_RESULT_BACKEND=redis://localhost:6379"; \
		echo "CELERY_BROKER_URL=redis://localhost:6379"; \
		echo "Created .env"; \
	fi

build: freeze
	BUILDKIT=1 docker build -t taskmate:latest . --cache-from=python:3.8.16-slim-bullseye

docker-dev:
	COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f ./docker-compose/docker-compose-dev.yaml down
	COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f ./docker-compose/docker-compose-dev.yaml up -d

docker:
	COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f ./docker-compose/docker-compose.yaml down
	COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f ./docker-compose/docker-compose.yaml up -d

dependencies:
	python -m pip install -r requirements.txt
	pip3 install -e .

sast:
	pip3 install bandit
	bandit -r web

test:
	python -m pytest tests/ --cov=.

debug:
	source venv/bin/activate; \
	flask --app web run --debug --host 0.0.0.0 --port 5001

run:
	source venv/bin/activate; \
	gunicorn 'web:create_app()'

db:
	flask --app web db migrate; \
	flask --app web db upgrade;

freeze:
	pip3 freeze > requirements.txt;
