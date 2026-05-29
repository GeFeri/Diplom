#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'python_manual_db'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'kuzinvano228'),
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432'),
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
"; do
    sleep 1
done
echo "PostgreSQL is ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn DiplomBogdan.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
