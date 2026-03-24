APP=run.py
DB=instance/users.db

POETRY := $(shell command -v poetry 2> /dev/null)

ifeq ($(POETRY),)
RUN=
else
RUN=poetry run
endif

run:
	@if [ -f "$(DB)" ]; then \
		echo "Existing database found. Stamping migration head..."; \
		$(RUN) flask db stamp head; \
		echo "Applying any new migrations..."; \
		$(RUN) flask db upgrade; \
	else \
		echo "No database found. Creating fresh database..."; \
		$(RUN) flask db upgrade; \
	fi
	@echo "Starting app..."
	$(RUN) python $(APP)