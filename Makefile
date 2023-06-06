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
		echo "Created .env"; \
	fi

build: freeze
	docker build -t taskmate:latest .

docker-dev: 
	docker-compose -f ./docker-compose/docker-compose-dev.yaml down
	docker-compose -f ./docker-compose/docker-compose-dev.yaml up -d

docker:
	docker-compose -f ./docker-compose/docker-compose.yaml down
	docker-compose -f ./docker-compose/docker-compose.yaml up -d

install: env
	virtualenv venv; \
	source venv/bin/activate; \
	pip3 install -r requirements.txt;

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
	rm instance/web.sqlite; \
	flask --app web init-db;

db-view:
	sqlite3 instance/web.sqlite;

freeze:
	pip3 freeze > requirements.txt;
