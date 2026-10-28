"""
Configuração do projeto Django da Questão 1 (API de biblioteca virtual).

Decisões:
- SQLite, como pede o enunciado: zero configuração e suficiente para o escopo.
- Django REST Framework + django-filter para consultas por título/autor.
- drf-spectacular gera o schema OpenAPI e a documentação interativa (/api/docs/).
- Variáveis sensíveis vêm do ambiente (ou de um .env na raiz do repositório, só para
  conveniência local); nada de segredo no código.
"""

import os
from pathlib import Path

# api_biblioteca/ (onde fica o manage.py e o db.sqlite3)
BASE_DIR = Path(__file__).resolve().parent.parent
# raiz do repositório (onde fica o .env)
REPO_DIR = BASE_DIR.parent


def _carregar_dotenv(caminho: Path) -> None:
    """Carrega KEY=VALUE de um .env sem sobrescrever variáveis já definidas.

    Implementação mínima de propósito: evita uma dependência extra só para o Django.
    """
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip())


_carregar_dotenv(REPO_DIR / ".env")

# Chave só para desenvolvimento local; em produção vem do ambiente.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-nao-use-em-producao")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = ["*"] if DEBUG else os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # terceiros
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    # projeto
    "livros",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Banco pedido no enunciado. O arquivo fica fora do versionamento (.gitignore).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Filtros declarados por view (django-filter), busca livre (?q=) e ordenação (?ordering=).
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "livros.filters.BuscaLivreFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # A API é pública no escopo do teste; em produção entraria autenticação (JWT/Keycloak).
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Biblioteca Virtual API",
    "DESCRIPTION": (
        "API para cadastrar e consultar livros (Questão 1 da prova de backend com foco em IA). "
        "Consulte livros por título ou autor com `?titulo=`, `?autor=` ou busca livre `?q=`."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
