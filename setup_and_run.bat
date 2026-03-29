@echo off

echo Applying any pending migrations...
flask db upgrade

echo Starting app...
python run.py
