#!/usr/bin/env python
"""Utilitário de linha de comando do Django para a API da biblioteca (Questão 1)."""

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover - só acontece com ambiente mal configurado
        raise ImportError(
            "Não foi possível importar o Django. Rode `uv sync` e use `uv run python manage.py`."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
