BUILD_TIME := $(shell date +%FT%T%z)
PROJECT    := $(shell basename $(PWD))

install:
	virtualenv venv; \
	source venv/bin/activate \
	pip install -r requirements.txt;

dependencies:
	python -m pip install -r requirements.txt
	pip install -e .

sast:
	pip install bandit
	bandit -r web

test:
	python -m pytest tests/ --cov=.

debug:
	source venv/bin/activate; \
	flask --app web run --debug --host 0.0.0.0  --port 5001

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
