
SHELL := /bin/bash

# Local environment
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
GUNICORN := $(VENV)/bin/gunicorn
SERVICE := benq-web.service

.PHONY: help install venv-recreate run run-debug service-install service-start service-stop service-status clean

help:
	@echo "Available targets:"
	@echo "  install          Create venv and install dependencies (requirements.txt)"
	@echo "  venv-recreate    Recreate the virtualenv and reinstall dependencies"
	@echo "  run              Run production server (gunicorn) using venv"
	@echo "  run-debug        Run the app directly with Python for development"
	@echo "  service-install  Install and enable systemd service (requires sudo)"
	@echo "  service-start    Start systemd service"
	@echo "  service-stop     Stop systemd service"
	@echo "  service-status   Show systemd service status"
	@echo "  clean            Remove virtualenv"

install:
	@test -f requirements.txt || (echo "requirements.txt not found" && exit 1)
	@# create venv only if missing
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
		echo "created $(VENV)"; \
	else \
		echo "$(VENV) already exists"; \
	fi
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

venv-recreate:
	@echo "Recreating virtualenv $(VENV)..."
	@rm -rf $(VENV)
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	@echo "Starting gunicorn (bind 0.0.0.0:5000)"
	$(GUNICORN) --bind 0.0.0.0:5000 --workers 1 Benq_Mw853ust_Webui:app

run-debug:
	@echo "Running with Python (debug)"
	$(PY) Benq_Mw853ust_Webui.py

service-install:
	@if [ ! -f $(SERVICE) ]; then echo "$(SERVICE) not found in repo"; exit 1; fi
	@sudo cp $(SERVICE) /etc/systemd/system/benq-web.service
	@sudo systemctl daemon-reload
	@sudo systemctl enable --now benq-web.service

service-start:
	@sudo systemctl start benq-web.service

service-stop:
	@sudo systemctl stop benq-web.service

service-status:
	@sudo systemctl status benq-web.service

clean:
	@echo "Removing virtualenv $(VENV)"
	@rm -rf $(VENV)

