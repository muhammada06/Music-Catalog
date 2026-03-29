APP=run.py

POETRY := $(shell command -v poetry 2> /dev/null)

ifeq ($(POETRY),)
RUN=
else
RUN=poetry run
endif

run:
	@echo "Applying any pending migrations..."
	@$(RUN) flask db upgrade
	@echo "Starting app..."
	$(RUN) python $(APP)