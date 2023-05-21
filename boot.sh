#!/bin/bash
source venv/bin/activate
exec gunicorn --access-logfile - --error-logfile - 'web:create_app()'