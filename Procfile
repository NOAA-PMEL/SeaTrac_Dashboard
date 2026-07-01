web: gunicorn app:server --workers 4
worker-default: celery -A tasks worker --loglevel=INFO --concurrency=2
worker-beat: celery -A tasks beat --loglevel=INFO
