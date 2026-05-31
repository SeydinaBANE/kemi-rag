.PHONY: up down serve ingest query lint typecheck test coverage security \
        precommit docker-build clean help

help:
	@echo "Usage:"
	@echo "  make up             Docker compose up -d"
	@echo "  make down           Docker compose down"
	@echo "  make serve          Lancer le serveur FastAPI en dev"
	@echo "  make ingest         Ingerer les documents"
	@echo "  make query q=...    Poser une question"
	@echo "  make lint           Ruff check"
	@echo "  make typecheck      Mypy check"
	@echo "  make test           Pytest"
	@echo "  make coverage       Pytest avec couverture"
	@echo "  make security       Bandit + Safety"
	@echo "  make precommit      Pre-commit run --all-files"
	@echo "  make docker-build   Docker compose build"
	@echo "  make clean          Nettoyer les artefacts"

up:
	docker compose up -d

down:
	docker compose down

serve:
	uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000

ingest:
	python cli.py ingest --dir documents/

query:
	python cli.py query "$(q)"

lint:
	ruff check app/ tests/ cli.py

typecheck:
	mypy app/ tests/ cli.py

test:
	pytest

coverage:
	pytest --cov --cov-report=html --cov-fail-under=50

security:
	bandit -r app/ cli.py
	safety check --full-report

precommit:
	pre-commit run --all-files

docker-build:
	docker compose build

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
