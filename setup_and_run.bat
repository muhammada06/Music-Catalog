@echo off

set FLASK_APP=run.py

echo Installing dependencies...
poetry install --no-interaction --quiet

echo Applying migrations...
poetry run flask db upgrade

echo Starting app...
poetry run python run.py
