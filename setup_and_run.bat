@echo off

IF EXIST instance\users.db (
    echo Existing database found. Stamping migration head...
    flask db stamp head
    echo Applying any new migrations...
    flask db upgrade
) ELSE (
    echo No database found. Creating fresh database...
    flask db upgrade
)

echo Starting app...
python run.py
