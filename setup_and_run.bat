@echo off

echo Applying any pending migrations...
poetry run flask db upgrade

echo Starting app...
poetry run python run.py
