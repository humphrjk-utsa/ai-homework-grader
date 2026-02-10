#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
python3 -c "
import socket, time, os
host = os.environ.get('POSTGRES_HOST', 'postgres')
port = int(os.environ.get('POSTGRES_PORT', 5432))
for i in range(30):
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        print(f'PostgreSQL is ready at {host}:{port}')
        break
    except (socket.error, ConnectionRefusedError):
        print(f'Waiting for {host}:{port}... ({i+1}/30)')
        time.sleep(2)
else:
    print('ERROR: PostgreSQL not available after 60s')
    exit(1)
"

echo "Running database migrations..."
cd /app/backend
flask db upgrade

echo "Ensuring storage directory..."
mkdir -p "${STORAGE_ROOT:-/app/storage}"

echo "Starting application..."
exec "$@"
