#!/bin/bash
source venv/bin/activate
exec celery -A core worker --loglevel=info
