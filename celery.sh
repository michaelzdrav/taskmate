#!/bin/bash
celery -A web.celery_app worker --loglevel=info