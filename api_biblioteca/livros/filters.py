"""Filtros de consulta da API de livros.

Duas formas de consultar, as duas pedidas no enunciado ("por título ou autor"):
- filtros nomeados: `?titulo=casmurro`, `?autor=machado` (podem ser combinados);
- busca livre: `?q=machado` procura em título E autor ao mesmo tempo.

As duas ignoram acentos e maiúsculas: `?titulo=cortico` acha "O Cortiço" e `?autor=ALUÍSIO`
acha "Aluísio Azevedo". O termo é normalizado do mesmo jeito que as colunas
`*_normalizado` do modelo, então a comparação é texto simples contra texto simples.
"""

import django_filters
from django.db.models import QuerySet
from rest_framework.filters import SearchFilter

from .models import Livro, normalizar


class LivroFilter(django_filters.FilterSet):
    """Filtros nomeados. Busca parcial, sem distinguir acentos nem maiúsculas."""

    titulo = django_filters.CharFilter(
        method="filtrar_titulo",
        help_text="Parte do título; ignora acentos e maiúsculas/minúsculas.",
    )
    autor = django_filters.CharFilter(
        method="filtrar_autor",
        help_text="Parte do nome do autor; ignora acentos e maiúsculas/minúsculas.",
    )
    ano = django_filters.NumberFilter(
        field_name="data_publicacao",
        lookup_expr="year",
        help_text="Ano de publicação exato.",
    )
    publicado_apos = django_filters.DateFilter(
        field_name="data_publicacao",
        lookup_expr="gte",
        help_text="Data mínima de publicação (AAAA-MM-DD).",
    )
    publicado_antes = django_filters.DateFilter(
        field_name="data_publicacao",
        lookup_expr="lte",
        help_text="Data máxima de publicação (AAAA-MM-DD).",
    )

    def filtrar_titulo(self, queryset: QuerySet, nome: str, valor: str) -> QuerySet:
        return queryset.filter(titulo_normalizado__contains=normalizar(valor))

    def filtrar_autor(self, queryset: QuerySet, nome: str, valor: str) -> QuerySet:
        return queryset.filter(autor_normalizado__contains=normalizar(valor))

    class Meta:
        model = Livro
        fields = ["titulo", "autor", "ano", "publicado_apos", "publicado_antes"]


class BuscaLivreFilter(SearchFilter):
    """SearchFilter do DRF com o parâmetro renomeado de `search` para `q` e termos normalizados.

    A view aponta `search_fields` para as colunas normalizadas; aqui o termo digitado
    passa pela mesma normalização, senão "memórias" nunca casaria com "memorias".
    """

    search_param = "q"
    search_title = "Busca livre"
    search_description = (
        "Texto procurado em título e autor ao mesmo tempo (parcial; ignora acentos e maiúsculas)."
    )

    def get_search_terms(self, request) -> list[str]:
        return [normalizar(termo) for termo in super().get_search_terms(request)]
