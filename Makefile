.PHONY: up down test lint format secret migrate

up:
	docker compose up --build

down:
	docker compose down

test:
	cd core && pytest

lint:
	cd core && flake8 .

format:
	cd core && black .

secret:
	python scripts/generate_secret_key.py

migrate:
	docker compose exec backend python manage.py migrate
