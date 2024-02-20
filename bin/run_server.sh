#!/bin/bash
# run_server.sh; runs the Flask server locally

FLASK_APP=app
FLASK_PORT=10465

cd "$(dirname "$0")"/.. || exit
echo "Starting Flask server..."

source .venv/bin/activate
flask --app $FLASK_APP run --host 0.0.0.0 --port $FLASK_PORT
