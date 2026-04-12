#The aplication runs using run.py
APP=run.py

#Check if the computer has poetry installed
POETRY := $(shell command -v poetry 2> /dev/null)

ifeq ($(POETRY),)
#If poetry not install make will ignore RUN
RUN=
else
#If poetry is installed make will use poetry run
RUN=poetry run
endif

#What happens when make or make run is called: Installs project dependencies -> Applies database migrations -> Starts the Flask application
run:
	@echo "Installing dependencies..."
	@$(RUN) poetry install --no-interaction
	@echo "Applying any pending migrations..."
	@$(RUN) flask db upgrade
	@echo "Starting app..."
	$(RUN) python $(APP)