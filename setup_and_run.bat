REM Prevents commands from being printed
@echo off

REM Sets the current flask app to be run using run.py
set FLASK_APP=run.py

REM Installs project dependencies
echo Installing dependencies...
poetry install --no-interaction --quiet

REM Applies database migrations
echo Applying migrations...
poetry run flask db upgrade

REM Starts the Flask application
echo Starting app...
poetry run python run.py
