install:
	virtualenv venv; \
	source venv/bin/activate \
	pip install -r requirements.txt;

dependencies:
	python -m pip install -r requirements.txt

test:
	pytest -v --cov

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
