#!/bin/bash
source venv/bin/activate

while ! [ "$(nc -vz $DATABASE_HOST $DATABASE_PORT 2>&1)" ]; do
    echo "Waiting for $DATABASE_HOST:$DATABASE_PORT..."
    sleep 30
done

echo "$DATABASE_HOST:$DATABASE_PORT is available."

flask --app web db migrate 
flask --app web db upgrade
exec gunicorn --access-logfile - --error-logfile - 'web:create_app()'
