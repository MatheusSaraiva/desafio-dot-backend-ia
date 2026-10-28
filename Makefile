# Atalhos para o dia a dia. Todos usam o ambiente do uv (`uv run`).
.PHONY: setup lint format test test-all run-api seed build-index search evaluate chat

setup:            ## instala dependências (torch só CPU) e cria o .env se não existir
	uv sync --all-groups
	@test -f .env || cp .env.example .env

lint:             ## ruff (lint + formatação)
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

test:             ## testes rápidos e offline (sem chaves, sem download de modelos)
	uv run pytest

test-all:         ## inclui integração (OpenAI) e o modelo real de embeddings
	uv run pytest -m "integration or slow or not (integration or slow)"

run-api:          ## Questão 1: sobe a API em http://127.0.0.1:8000/api/docs/
	uv run python api_biblioteca/manage.py migrate
	uv run python api_biblioteca/manage.py runserver

seed:             ## Questão 1: carrega 10 livros de exemplo
	uv run python api_biblioteca/manage.py migrate
	uv run python api_biblioteca/manage.py loaddata livros

build-index:      ## Questão 3: gera embeddings e o índice FAISS do corpus
	uv run python -m busca_semantica.cli build-index

search:           ## Questão 3: ex. make search Q="como percorrer uma lista"
	uv run python -m busca_semantica.cli search "$(Q)"

evaluate:         ## Questão 3: recall@k / MRR da busca semântica vs BM25
	uv run python -m busca_semantica.cli evaluate

chat:             ## Questão 2: chatbot no terminal (precisa de OPENAI_API_KEY no .env)
	uv run python -m chatbot_python.cli
