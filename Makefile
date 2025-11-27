SHELL := /bin/bash

IMAGE := controlleur_projecteur
CONTAINER := controlleur_projecteur

.PHONY: help build rebuild run run-dev compose-up compose-down logs shell clean

help:
	@echo "Available targets:"
	@echo "  build        Build Docker image"
	@echo "  rebuild      Build image without cache"
	@echo "  run          Run container (name=$(CONTAINER))"
	@echo "  run-dev      Run container with project bind-mounted for live edits"
	@echo "  compose-up   Start services with docker-compose"
	@echo "  compose-down Stop services started by docker-compose"
	@echo "  logs         Follow docker-compose logs"
	@echo "  shell        Open a shell in the running service (uses docker-compose)"
	@echo "  clean        Remove container and image"

build:
	docker build -t $(IMAGE) .

rebuild:
	docker build --no-cache -t $(IMAGE) .

run:
	docker run --rm --name $(CONTAINER) -p 5000:5000 $(IMAGE)

run-dev:
	docker run --rm --name $(CONTAINER) -p 5000:5000 -v $(PWD):/app:delegated $(IMAGE)

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec web /bin/bash

clean:
	- docker rm -f $(CONTAINER) 2>/dev/null || true
	- docker rmi $(IMAGE) 2>/dev/null || true
