install:
	virtualenv venv; \
	source venv/bin/activate \
	pip install -r requirements.txt;

dependencies:
	pip install -r requirements.txt

coverage:
	python -m pytest tests/ --cov=.

test: coverage
	python -m pytest tests/ -v

run:
	source venv/bin/activate; \
	flask --app web run --debug --host 0.0.0.0  --port 5001

db: 
	rm instance/web.sqlite; \
	flask --app web init-db;

db-view:
	sqlite3 instance/web.sqlite;

freeze:
	pip3 freeze > requirements.txt;
